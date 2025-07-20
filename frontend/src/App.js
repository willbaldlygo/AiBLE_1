import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload';
import DocumentList from './components/DocumentList';
import ChatInterface from './components/ChatInterface';
import { getDocuments, deleteDocument, chatWithDocuments } from './utils/api';

function App() {
  const [documents, setDocuments] = useState([]);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(true);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setIsLoadingDocuments(true);
      const docs = await getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Failed to load documents:', error);
      showNotification('Could not connect to the server. Please make sure it is running.', 'error');
      setDocuments([]);
    } finally {
      setIsLoadingDocuments(false);
    }
  };

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  

  const handleUploadSuccess = (newDocument) => {
    setDocuments(prev => [newDocument, ...prev]);
    showNotification(`Successfully uploaded "${newDocument.name}"`, 'success');
  };

  const handleUploadError = (error) => {
    showNotification(error, 'error');
  };

  const handleDeleteDocument = async (documentId) => {
    try {
      await deleteDocument(documentId);
      setDocuments(prev => prev.filter(doc => doc.id !== documentId));
      showNotification('Document deleted successfully', 'success');
    } catch (error) {
      console.error('Failed to delete document:', error);
      showNotification('Failed to delete document', 'error');
    }
  };

  const handleSendMessage = async (question) => {
    setIsChatLoading(true);
    try {
      const response = await chatWithDocuments(question);
      return response;
    } catch (error) {
      console.error('Chat error:', error);
      throw error;
    } finally {
      setIsChatLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-able-primary">
      {/* Header */}
      <header className="bg-able-cardBg shadow-card border-b-2 border-able-cardBorder">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-able-primary rounded-card flex items-center justify-center shadow-card">
                <svg className="w-7 h-7 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-able-textPrimary">Able2</h1>
                <p className="text-able-textSecondary">PDF Research Assistant</p>
              </div>
            </div>
            
            <div className="bg-able-primary text-white px-4 py-2 rounded-card shadow-card">
              <span className="font-semibold">{documents.length} document{documents.length !== 1 ? 's' : ''} uploaded</span>
            </div>
          </div>
        </div>
      </header>

      {/* Notification */}
      {notification && (
        <div className="fixed top-6 right-6 z-50 max-w-sm">
          <div
            className={`rounded-card p-4 shadow-card border-2 ${
              notification.type === 'success'
                ? 'bg-green-50 border-green-300 text-green-800'
                : notification.type === 'error'
                ? 'bg-red-50 border-red-300 text-red-800'
                : 'bg-blue-50 border-blue-300 text-blue-800'
            }`}
          >
            <div className="flex items-start">
              <div className="flex-shrink-0">
                {notification.type === 'success' && (
                  <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                )}
                {notification.type === 'error' && (
                  <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-semibold">{notification.message}</p>
              </div>
              <button
                onClick={() => setNotification(null)}
                className="ml-3 flex-shrink-0 text-gray-400 hover:text-gray-600"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column */}
          <div className="space-y-6">
            <FileUpload
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
            />
            
            <DocumentList
              documents={documents}
              onDeleteDocument={handleDeleteDocument}
              isLoading={isLoadingDocuments}
            />
          </div>

          {/* Right Column */}
          <div>
            <ChatInterface
              onSendMessage={handleSendMessage}
              isLoading={isChatLoading}
              hasDocuments={documents.length > 0}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-able-cardBg border-t-2 border-able-cardBorder mt-16 shadow-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-able-textPrimary font-semibold mb-2">
              Able2 PDF Research Assistant
            </p>
            <p className="text-able-textSecondary text-sm">
              Upload PDFs, ask questions, get intelligent responses with source attribution
            </p>
            <p className="text-able-textSecondary text-sm mt-1">
              Powered by Claude AI and vector search technology
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;