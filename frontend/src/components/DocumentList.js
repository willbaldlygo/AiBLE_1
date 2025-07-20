import React, { useState } from 'react';

const DocumentList = ({ documents, onDeleteDocument, isLoading }) => {
  const [deletingId, setDeletingId] = useState(null);

  const handleDelete = async (documentId, documentName) => {
    if (window.confirm(`Are you sure you want to delete "${documentName}"?`)) {
      setDeletingId(documentId);
      try {
        await onDeleteDocument(documentId);
      } finally {
        setDeletingId(null);
      }
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  if (isLoading) {
    return (
      <div className="card">
        <h2 className="heading-secondary">Uploaded Documents</h2>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-10 w-10 border-b-3 border-able-primary"></div>
          <span className="ml-4 text-able-textSecondary font-medium">Loading documents...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="heading-secondary">
        Uploaded Documents ({documents.length})
      </h2>
      
      {documents.length === 0 ? (
        <div className="text-center py-12">
          <div className="mx-auto w-20 h-20 text-able-textSecondary mb-6">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <p className="text-xl font-semibold text-able-textPrimary mb-2">No documents uploaded yet</p>
          <p className="text-body">Upload a PDF to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="bg-able-cardBg border-2 border-able-cardBorder rounded-card p-6 hover:shadow-card transition-all duration-200"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="w-12 h-12 bg-able-primary rounded-card flex items-center justify-center shadow-card">
                      <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-semibold text-able-textPrimary truncate mb-1">
                        {doc.name}
                      </h3>
                      <div className="flex items-center space-x-3 text-small">
                        <span className="bg-able-cardBorder px-2 py-1 rounded text-able-textSecondary">{formatFileSize(doc.file_size)}</span>
                        <span className="text-able-textSecondary">{formatDate(doc.created_at)}</span>
                      </div>
                    </div>
                  </div>
                  
                  <p className="text-body line-clamp-3 bg-gray-50 p-3 rounded-card border border-able-cardBorder">
                    {doc.summary}
                  </p>
                </div>
                
                <button
                  onClick={() => handleDelete(doc.id, doc.name)}
                  disabled={deletingId === doc.id}
                  className="ml-4 p-3 text-able-textSecondary hover:text-red-600 hover:bg-red-50 rounded-card border-2 border-transparent hover:border-red-200 transition-all duration-200 disabled:opacity-50"
                  title="Delete document"
                >
                  {deletingId === doc.id ? (
                    <div className="w-5 h-5 animate-spin rounded-full border-2 border-gray-300 border-t-red-600"></div>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DocumentList;