import os
import json
import logging
from typing import List, Optional, Dict
from datetime import datetime
from models import Document, DocumentSummary
from vector_store import VectorStore
from document_processor import PDFProcessor

logger = logging.getLogger(__name__)

class DocumentManager:
    def __init__(self, sources_path: str, vector_store: VectorStore, pdf_processor: PDFProcessor):
        self.metadata_path = os.path.join(sources_path, '..', 'document_metadata.json')
        self.vector_store = vector_store
        self.pdf_processor = pdf_processor
        self.documents = self._load_metadata()
        logger.info(f"Loaded {len(self.documents)} documents from metadata")

    def _load_metadata(self) -> Dict[str, Document]:
        if not os.path.exists(self.metadata_path):
            return {}
        try:
            with open(self.metadata_path, 'r') as f:
                data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error reading document metadata file: {e}")
            return {}

        documents = {}
        for doc_id, doc_data in data.items():
            try:
                # Ensure created_at is a datetime object
                if isinstance(doc_data.get('created_at'), str):
                    doc_data['created_at'] = datetime.fromisoformat(doc_data['created_at'])
                
                # Validate and create Document object
                documents[doc_id] = Document(**doc_data)
            except Exception as e:
                logger.warning(f"Skipping invalid document metadata for ID {doc_id}: {e}")
        
        return documents

    def _save_metadata(self):
        try:
            with open(self.metadata_path, 'w') as f:
                # Convert Document objects to dictionaries for JSON serialization
                data_to_save = {doc_id: doc.dict() for doc_id, doc in self.documents.items()}
                json.dump(data_to_save, f, indent=4, default=str)
        except IOError as e:
            logger.error(f"Error saving document metadata: {e}")

    def add_document(self, document: Document) -> bool:
        if document.id in self.documents:
            logger.warning(f"Document with ID {document.id} already exists.")
            return False
        self.documents[document.id] = document
        self._save_metadata()
        return True

    def get_document(self, doc_id: str) -> Optional[Document]:
        return self.documents.get(doc_id)

    def get_all_documents(self) -> List[DocumentSummary]:
        summaries = []
        for doc in self.documents.values():
            summaries.append(
                DocumentSummary(
                    id=doc.id,
                    name=doc.name,
                    file_type=doc.file_type,
                    summary=doc.summary,
                    created_at=doc.created_at,
                    file_size=doc.file_size,
                )
            )
        # Sort by creation date, newest first
        return sorted(summaries, key=lambda x: x.created_at, reverse=True)

    def delete_document(self, doc_id: str) -> bool:
        document = self.get_document(doc_id)
        if not document:
            return False

        # 1. Delete from vector store
        if not self.vector_store.delete_document(doc_id):
            logger.error(f"Failed to delete document {doc_id} from vector store.")
            # Continue with other deletions anyway

        # 2. Delete file from sources
        if not self.pdf_processor.delete_file(document.file_path):
            logger.error(f"Failed to delete file {document.file_path}.")

        # 3. Delete from metadata
        if doc_id in self.documents:
            del self.documents[doc_id]
            self._save_metadata()
            logger.info(f"Successfully deleted document {doc_id}")
            return True
        return False

    def get_document_count(self) -> int:
        return len(self.documents)
