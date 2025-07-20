import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional
import logging
import os
from models import Document, DocumentChunk, SourceInfo

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create directory if it doesn't exist
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Initialized vector store at {db_path}")
    
    def add_document(self, document: Document) -> bool:
        """
        Add a document and its chunks to the vector store.
        """
        try:
            # Prepare data for ChromaDB
            chunk_texts = [chunk.content for chunk in document.chunks]
            chunk_ids = [chunk.id for chunk in document.chunks]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(chunk_texts).tolist()
            
            # Prepare metadata for each chunk
            metadatas = []
            for chunk in document.chunks:
                metadata = {
                    "document_id": document.id,
                    "document_name": document.name,
                    "chunk_index": chunk.chunk_index,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                    "file_type": document.file_type
                }
                metadatas.append(metadata)
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=chunk_texts,
                metadatas=metadatas,
                ids=chunk_ids
            )
            
            logger.info(f"Added document {document.name} with {len(document.chunks)} chunks to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document to vector store: {str(e)}")
            return False
    
    def search(self, query: str, n_results: int = 5, document_ids: Optional[List[str]] = None) -> List[SourceInfo]:
        """
        Search for relevant chunks based on query.
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Prepare where clause for filtering by document IDs
            where_clause = None
            if document_ids:
                where_clause = {"document_id": {"$in": document_ids}}
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Convert results to SourceInfo objects
            sources = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Convert distance to relevance score (higher is better)
                    relevance_score = max(0, 1 - distance)
                    
                    source = SourceInfo(
                        document_id=metadata['document_id'],
                        document_name=metadata['document_name'],
                        chunk_content=doc,
                        relevance_score=relevance_score
                    )
                    sources.append(source)
            
            logger.info(f"Search query '{query}' returned {len(sources)} results")
            return sources
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete all chunks belonging to a document from the vector store.
        """
        try:
            # Get all chunk IDs for this document
            results = self.collection.get(
                where={"document_id": document_id},
                include=["metadatas"]
            )
            
            if results['ids']:
                # Delete all chunks for this document
                self.collection.delete(
                    where={"document_id": document_id}
                )
                logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
                return True
            else:
                logger.warning(f"No chunks found for document {document_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting document from vector store: {str(e)}")
            return False
    
    def get_document_count(self) -> int:
        """
        Get the total number of unique documents in the vector store.
        """
        try:
            results = self.collection.get(include=["metadatas"])
            document_ids = set()
            
            if results['metadatas']:
                for metadata in results['metadatas']:
                    document_ids.add(metadata['document_id'])
            
            return len(document_ids)
            
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            return 0
    
    def get_all_documents(self) -> List[Dict]:
        """
        Get summary information for all documents in the vector store.
        """
        try:
            results = self.collection.get(include=["metadatas"])
            documents = {}
            
            if results['metadatas']:
                for metadata in results['metadatas']:
                    doc_id = metadata['document_id']
                    if doc_id not in documents:
                        documents[doc_id] = {
                            'id': doc_id,
                            'name': metadata['document_name'],
                            'file_type': metadata['file_type'],
                            'chunk_count': 0
                        }
                    documents[doc_id]['chunk_count'] += 1
            
            return list(documents.values())
            
        except Exception as e:
            logger.error(f"Error getting all documents: {str(e)}")
            return []
    
    def health_check(self) -> Dict[str, any]:
        """
        Check the health of the vector store.
        """
        try:
            # Test basic operations
            chunk_count = self.collection.count()
            document_count = self.get_document_count()
            
            return {
                "status": "healthy",
                "chunk_count": chunk_count,
                "document_count": document_count,
                "embedding_model": "all-MiniLM-L6-v2"
            }
            
        except Exception as e:
            logger.error(f"Vector store health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def clear_all(self) -> bool:
        """
        Clear all documents from the vector store.
        WARNING: This will delete all data.
        """
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name="documents")
            self.collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("Cleared all documents from vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")
            return False