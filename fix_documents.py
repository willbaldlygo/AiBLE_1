#!/usr/bin/env python3

"""
Script to diagnose and fix document processing issues in Able2
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.document_manager import DocumentManager
from backend.vector_store import VectorStore
from backend.document_processor import PDFProcessor

def main():
    # Load environment variables
    load_dotenv('backend/.env')
    
    # Initialize components
    sources_path = './sources'
    vector_db_path = './data/vectordb'
    
    print("🔍 Diagnosing Able2 document processing...")
    print()
    
    try:
        vector_store = VectorStore(vector_db_path)
        pdf_processor = PDFProcessor(sources_path)
        doc_manager = DocumentManager(sources_path, vector_store, pdf_processor)
        
        # Check metadata file
        print("📄 Document Metadata:")
        with open('document_metadata.json', 'r') as f:
            metadata = json.load(f)
        
        for doc_id, doc_info in metadata.items():
            print(f"  • {doc_info['name']}")
            print(f"    - ID: {doc_id}")
            print(f"    - Chunks: {doc_info['chunk_count']}")
            print(f"    - File exists: {os.path.exists(doc_info['file_path'])}")
            print()
        
        # Check vector store
        print("🔍 Vector Store Contents:")
        vector_docs = vector_store.get_all_documents()
        print(f"  Documents in vector store: {len(vector_docs)}")
        for doc in vector_docs:
            print(f"  • {doc}")
        print()
        
        # Find documents with 0 chunks and reprocess them
        print("🔧 Fixing documents with 0 chunks...")
        for doc_id, doc_info in metadata.items():
            if doc_info['chunk_count'] == 0:
                print(f"  ⚠️  Found document with 0 chunks: {doc_info['name']}")
                
                if os.path.exists(doc_info['file_path']):
                    print(f"  🔄 Reprocessing {doc_info['name']}...")
                    
                    # Remove from vector store if exists
                    vector_store.delete_document(doc_id)
                    
                    # Reprocess the document
                    document = pdf_processor.process_pdf(doc_info['file_path'], doc_info['name'])
                    
                    # Add to vector store
                    if vector_store.add_document(document):
                        print(f"  ✅ Successfully reprocessed {doc_info['name']} with {len(document.chunks)} chunks")
                        
                        # Update metadata
                        doc_manager.documents_db[doc_id] = document
                        doc_manager._save_metadata()
                    else:
                        print(f"  ❌ Failed to add {doc_info['name']} to vector store")
                else:
                    print(f"  ❌ File not found: {doc_info['file_path']}")
        
        print()
        print("✅ Document processing diagnosis and repair complete!")
        
        # Final verification
        print("🔍 Final Status:")
        with open('document_metadata.json', 'r') as f:
            updated_metadata = json.load(f)
        
        for doc_id, doc_info in updated_metadata.items():
            status = "✅" if doc_info['chunk_count'] > 0 else "❌"
            print(f"  {status} {doc_info['name']}: {doc_info['chunk_count']} chunks")
        
    except Exception as e:
        print(f"❌ Error during diagnosis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()