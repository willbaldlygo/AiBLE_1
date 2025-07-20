import React, { useState, useRef } from 'react';
import { uploadDocument } from '../utils/api';

const FileUpload = ({ onUploadSuccess, onUploadError }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadQueue, setUploadQueue] = useState([]);
  const [currentlyUploading, setCurrentlyUploading] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    const pdfFiles = files.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length === 0) {
      onUploadError('Please upload only PDF files');
      return;
    }

    // Add multiple files to queue
    handleMultipleFiles(pdfFiles);
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    const pdfFiles = files.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length === 0) {
      onUploadError('Please upload only PDF files');
      return;
    }

    // Add multiple files to queue
    handleMultipleFiles(pdfFiles);
    e.target.value = '';
  };

  const handleMultipleFiles = (files) => {
    // Validate file sizes
    const oversizedFiles = files.filter(file => file.size > 50 * 1024 * 1024);
    if (oversizedFiles.length > 0) {
      onUploadError(`${oversizedFiles.length} file(s) exceed 50MB limit and will be skipped`);
      files = files.filter(file => file.size <= 50 * 1024 * 1024);
    }

    if (files.length === 0) return;

    // Add files to upload queue
    const queueItems = files.map((file, index) => ({
      id: Date.now() + index,
      file,
      status: 'pending', // pending, uploading, completed, failed
      progress: 0
    }));

    setUploadQueue(prev => [...prev, ...queueItems]);
    
    // Start processing queue if not already uploading
    if (!isUploading) {
      processUploadQueue([...uploadQueue, ...queueItems]);
    }
  };

  const processUploadQueue = async (queue) => {
    if (queue.length === 0) return;

    setIsUploading(true);
    
    for (const item of queue) {
      if (item.status !== 'pending') continue;
      
      setCurrentlyUploading(item);
      setUploadQueue(prev => 
        prev.map(q => q.id === item.id ? { ...q, status: 'uploading' } : q)
      );

      try {
        const result = await uploadDocument(item.file);
        
        setUploadQueue(prev => 
          prev.map(q => q.id === item.id ? { ...q, status: 'completed', progress: 100 } : q)
        );
        
        onUploadSuccess(result);
        
      } catch (error) {
        const errorMessage = error.response?.data?.detail || `Failed to upload ${item.file.name}`;
        
        setUploadQueue(prev => 
          prev.map(q => q.id === item.id ? { ...q, status: 'failed' } : q)
        );
        
        onUploadError(errorMessage);
      }
    }

    setIsUploading(false);
    setCurrentlyUploading(null);
    
    // Clear completed items after a delay
    setTimeout(() => {
      setUploadQueue(prev => prev.filter(item => item.status === 'pending'));
    }, 3000);
  };


  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="card">
      <h2 className="heading-secondary">Upload PDF Document</h2>
      
      <div
        className={`
          border-2 border-dashed rounded-card p-10 text-center cursor-pointer transition-all duration-200
          ${isDragging 
            ? 'border-able-primary bg-primary-50 shadow-card' 
            : 'border-able-cardBorder hover:border-able-primary hover:shadow-card'
          }
          ${isUploading ? 'pointer-events-none opacity-60' : ''}
          bg-able-cardBg
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={openFileDialog}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          multiple
          onChange={handleFileSelect}
          className="hidden"
        />
        
        <div className="space-y-6">
          <div className="mx-auto w-20 h-20 text-able-textSecondary">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
          </div>
          
          {isUploading ? (
            <div className="space-y-3">
              <div className="text-able-primary font-semibold text-lg">
                {currentlyUploading ? `Uploading ${currentlyUploading.file.name}...` : 'Processing uploads...'}
              </div>
              <div className="w-full bg-able-cardBorder rounded-full h-3">
                <div className="bg-able-primary h-3 rounded-full animate-pulse w-3/4 shadow-card"></div>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="text-xl font-semibold text-able-textPrimary">
                Drop your PDFs here, or click to browse
              </div>
              <div className="text-body">
                Supports multiple PDF files up to 50MB each
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Upload Queue Display */}
      {uploadQueue.length > 0 && (
        <div className="mt-6 bg-able-cardBg border border-able-cardBorder rounded-card p-4">
          <h3 className="text-lg font-semibold text-able-textPrimary mb-3">Upload Queue</h3>
          <div className="space-y-2">
            {uploadQueue.map((item) => (
              <div key={item.id} className="flex items-center justify-between p-2 bg-white rounded border">
                <div className="flex-1">
                  <div className="text-sm font-medium text-able-textPrimary truncate">
                    {item.file.name}
                  </div>
                  <div className="text-xs text-able-textSecondary">
                    {(item.file.size / (1024 * 1024)).toFixed(1)} MB
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <div className={`px-2 py-1 rounded text-xs font-medium ${
                    item.status === 'pending' ? 'bg-gray-100 text-gray-600' :
                    item.status === 'uploading' ? 'bg-blue-100 text-blue-600' :
                    item.status === 'completed' ? 'bg-green-100 text-green-600' :
                    'bg-red-100 text-red-600'
                  }`}>
                    {item.status === 'pending' ? 'Waiting' :
                     item.status === 'uploading' ? 'Uploading' :
                     item.status === 'completed' ? 'Complete' : 'Failed'}
                  </div>
                  {item.status === 'uploading' && (
                    <div className="w-8 h-8">
                      <svg className="animate-spin h-4 w-4 text-able-primary" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="mt-6 bg-able-cardBg border border-able-cardBorder rounded-card p-4">
        <div className="text-small space-y-1">
          <p className="flex items-center"><span className="text-able-primary mr-2">•</span>Only PDF files are supported</p>
          <p className="flex items-center"><span className="text-able-primary mr-2">•</span>Maximum file size: 50MB per file</p>
          <p className="flex items-center"><span className="text-able-primary mr-2">•</span>Multiple files can be uploaded simultaneously</p>
          <p className="flex items-center"><span className="text-able-primary mr-2">•</span>Files are processed locally and securely</p>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;