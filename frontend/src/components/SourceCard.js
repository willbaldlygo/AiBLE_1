import React from 'react';

const SourceCard = ({ source }) => {
  const truncateText = (text, maxLength = 200) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const formatRelevanceScore = (score) => {
    return Math.round(score * 100);
  };

  return (
    <div className="bg-able-cardBg border-2 border-able-cardBorder rounded-card p-4 mb-4 shadow-card">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className="w-3 h-3 bg-able-primary rounded-full shadow-card"></div>
          <span className="text-sm font-semibold text-able-textPrimary">
            {source.document_name}
          </span>
        </div>
        <div className="bg-able-primary text-white text-xs px-2 py-1 rounded font-medium">
          {formatRelevanceScore(source.relevance_score)}% relevant
        </div>
      </div>
      
      <div className="text-small text-able-textSecondary leading-relaxed bg-gray-50 p-3 rounded-card border border-able-cardBorder">
        {truncateText(source.chunk_content)}
      </div>
    </div>
  );
};

export default SourceCard;