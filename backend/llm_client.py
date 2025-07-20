import anthropic
from typing import List, Optional
import logging
from datetime import datetime
from models import SourceInfo, ChatResponse

logger = logging.getLogger(__name__)


class ClaudeClient:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-sonnet-20240229"
        logger.info("Initialized Claude client")
    
    def generate_response(self, question: str, sources: List[SourceInfo]) -> ChatResponse:
        """
        Generate a response to a question using relevant source information.
        """
        try:
            # Prepare context from sources
            context = self._prepare_context(sources)
            
            # Create the prompt
            prompt = self._create_prompt(question, context)
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            answer = response.content[0].text
            
            # Create response object
            chat_response = ChatResponse(
                answer=answer,
                sources=sources,
                timestamp=datetime.now()
            )
            
            logger.info(f"Generated response for question: {question[:50]}...")
            return chat_response
            
        except Exception as e:
            logger.error(f"Error generating Claude response: {str(e)}")
            # Return error response
            return ChatResponse(
                answer=f"I apologize, but I encountered an error while processing your question: {str(e)}",
                sources=[],
                timestamp=datetime.now()
            )
    
    def _prepare_context(self, sources: List[SourceInfo]) -> str:
        """
        Prepare context string from source information.
        """
        if not sources:
            return "No relevant documents found."
        
        context_parts = []
        for i, source in enumerate(sources, 1):
            context_part = f"""
Source {i} (from {source.document_name}):
{source.chunk_content}
---
"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, question: str, context: str) -> str:
        """
        Create a well-structured prompt for Claude.
        """
        prompt = f"""You are a helpful research assistant. Answer the user's question based on the provided source documents. 

IMPORTANT INSTRUCTIONS:
1. Base your answer primarily on the information provided in the sources
2. If the sources don't contain enough information to fully answer the question, say so
3. Be specific and cite which sources support your statements
4. Keep your response concise but comprehensive
5. If you need to make inferences, clearly distinguish them from facts stated in the sources

CONTEXT FROM DOCUMENTS:
{context}

USER QUESTION: {question}

Please provide a helpful and accurate response based on the source documents provided."""

        return prompt
    
    def generate_document_summary(self, text_content: str, document_name: str) -> str:
        """
        Generate a summary for a document using Claude.
        """
        try:
            # Limit text content for summary (first 2000 characters)
            limited_content = text_content[:2000]
            if len(text_content) > 2000:
                limited_content += "..."
            
            prompt = f"""Please provide a concise summary (2-3 sentences) of the following document content from "{document_name}":

{limited_content}

Summary:"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            summary = response.content[0].text.strip()
            logger.info(f"Generated summary for document: {document_name}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating document summary: {str(e)}")
            return f"Summary could not be generated. Document content extracted from {document_name}."
    
    def test_connection(self) -> bool:
        """
        Test the connection to Claude API.
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[
                    {
                        "role": "user",
                        "content": "Hello"
                    }
                ]
            )
            
            logger.info("Claude API connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Claude API connection test failed: {str(e)}")
            return False