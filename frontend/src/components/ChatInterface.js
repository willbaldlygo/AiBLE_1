import React, { useState, useRef, useEffect } from 'react';
import SourceCard from './SourceCard';

const ChatInterface = ({ onSendMessage, isLoading, hasDocuments }) => {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!question.trim() || isLoading) return;
    
    if (!hasDocuments) {
      alert('Please upload at least one PDF document before asking questions.');
      return;
    }

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: question.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setQuestion('');

    try {
      const response = await onSendMessage(userMessage.content);
      
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.answer,
        sources: response.sources,
        timestamp: new Date(response.timestamp)
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'Sorry, I encountered an error while processing your question. Please try again.',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const clearMessages = () => {
    if (window.confirm('Are you sure you want to clear the chat history?')) {
      setMessages([]);
    }
  };

  return (
    <div className="card h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <h2 className="heading-secondary">Chat with Documents</h2>
        {messages.length > 0 && (
          <button
            onClick={clearMessages}
            className="btn-secondary text-sm py-2 px-4"
          >
            Clear chat
          </button>
        )}
      </div>

      <div className="flex-1 flex flex-col min-h-0">
        <div className="flex-1 overflow-y-auto mb-6 space-y-6 max-h-96 bg-gray-50 rounded-card p-4 border-2 border-able-cardBorder">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <div className="mx-auto w-20 h-20 text-able-textSecondary mb-6">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
              </div>
              <p className="text-xl font-semibold text-able-textPrimary mb-2">Ready to answer your questions</p>
              <p className="text-body">
                {hasDocuments 
                  ? "Ask anything about your uploaded documents"
                  : "Upload a PDF document to start chatting"
                }
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className="space-y-4">
                <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div
                    className={`max-w-md px-5 py-3 rounded-card shadow-card ${
                      message.type === 'user'
                        ? 'bg-able-primary text-white'
                        : message.type === 'error'
                        ? 'bg-red-100 text-red-800 border-2 border-red-200'
                        : 'bg-able-cardBg text-able-textPrimary border-2 border-able-cardBorder'
                    }`}
                  >
                    <div className="text-sm leading-relaxed">{message.content}</div>
                    <div
                      className={`text-xs mt-2 opacity-75 ${
                        message.type === 'user' ? 'text-white' : 'text-able-textSecondary'
                      }`}
                    >
                      {formatTime(message.timestamp)}
                    </div>
                  </div>
                </div>

                {message.sources && message.sources.length > 0 && (
                  <div className="ml-0">
                    <div className="text-sm font-semibold text-able-textPrimary mb-3 flex items-center">
                      <div className="w-2 h-2 bg-able-primary rounded-full mr-2"></div>
                      Sources:
                    </div>
                    <div className="space-y-3">
                      {message.sources.map((source, index) => (
                        <SourceCard key={index} source={source} />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-able-cardBg text-able-textPrimary max-w-md px-5 py-3 rounded-card shadow-card border-2 border-able-cardBorder">
                <div className="flex items-center space-x-3">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-able-primary rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-able-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-able-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-sm font-medium">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="flex space-x-4">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder={hasDocuments ? "Ask a question about your documents..." : "Upload a document first"}
            className="input-field flex-1"
            disabled={isLoading || !hasDocuments}
          />
          <button
            type="submit"
            disabled={!question.trim() || isLoading || !hasDocuments}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed px-6 py-3"
          >
            {isLoading ? (
              <div className="w-5 h-5 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;