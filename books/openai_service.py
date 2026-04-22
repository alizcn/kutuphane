"""
OpenAI API Service Module
Handles all OpenAI API interactions for book recommendations and analysis.
"""

import logging
from typing import Optional, Dict, Any
from django.conf import settings
from openai import OpenAI, APIError, AuthenticationError, RateLimitError

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service class for OpenAI API interactions."""
    
    def __init__(self):
        """Initialize OpenAI client with API key from settings."""
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        
        if not self.api_key:
            logger.warning("OpenAI API key is not configured in settings")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
    
    def is_configured(self) -> bool:
        """Check if OpenAI service is properly configured."""
        return self.client is not None and self.api_key != ""
    
    def generate_book_recommendation(
        self, 
        user_preferences: str,
        language: str = "Turkish"
    ) -> Optional[str]:
        """
        Generate book recommendations based on user preferences.
        
        Args:
            user_preferences: Description of user's reading preferences
            language: Response language (default: Turkish)
            
        Returns:
            Generated recommendation text or None if API call fails
        """
        if not self.is_configured():
            logger.error("OpenAI service is not configured")
            return None
        
        try:
            prompt = f"""
            Based on the following reading preferences, suggest 3-5 books with brief descriptions.
            Language: {language}
            
            User preferences: {user_preferences}
            
            Format the response as a numbered list with book title, author, and a brief description.
            """
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return message.content[0].text
            
        except AuthenticationError as e:
            logger.error(f"OpenAI Authentication Error: {e}")
            return None
        except RateLimitError as e:
            logger.error(f"OpenAI Rate Limit Error: {e}")
            return None
        except APIError as e:
            logger.error(f"OpenAI API Error: {e}")
            return None
    
    def generate_book_summary(
        self, 
        book_title: str, 
        book_author: str,
        language: str = "Turkish"
    ) -> Optional[str]:
        """
        Generate a summary for a given book.
        
        Args:
            book_title: Title of the book
            book_author: Author of the book
            language: Response language (default: Turkish)
            
        Returns:
            Generated summary or None if API call fails
        """
        if not self.is_configured():
            logger.error("OpenAI service is not configured")
            return None
        
        try:
            prompt = f"""
            Please provide a concise summary (2-3 paragraphs) of the book "{book_title}" by {book_author}.
            Language: {language}
            
            Include main plot points and key themes.
            """
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return message.content[0].text
            
        except AuthenticationError as e:
            logger.error(f"OpenAI Authentication Error: {e}")
            return None
        except RateLimitError as e:
            logger.error(f"OpenAI Rate Limit Error: {e}")
            return None
        except APIError as e:
            logger.error(f"OpenAI API Error: {e}")
            return None
    
    def analyze_book_review(
        self, 
        review_text: str,
        language: str = "Turkish"
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze a book review and extract sentiment and key themes.
        
        Args:
            review_text: The review text to analyze
            language: Response language (default: Turkish)
            
        Returns:
            Dictionary with sentiment and key themes, or None if API call fails
        """
        if not self.is_configured():
            logger.error("OpenAI service is not configured")
            return None
        
        try:
            prompt = f"""
            Analyze the following book review and provide:
            1. Sentiment (positive/negative/neutral)
            2. Key themes mentioned
            3. Overall rating (1-5)
            
            Language: {language}
            Review: "{review_text}"
            
            Provide the response in JSON format.
            """
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            import json
            response_text = message.content[0].text
            
            # Try to extract JSON from the response
            try:
                # Try to find JSON in the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return {"raw_response": response_text}
            except json.JSONDecodeError:
                return {"raw_response": response_text}
            
        except AuthenticationError as e:
            logger.error(f"OpenAI Authentication Error: {e}")
            return None
        except RateLimitError as e:
            logger.error(f"OpenAI Rate Limit Error: {e}")
            return None
        except APIError as e:
            logger.error(f"OpenAI API Error: {e}")
            return None
    
    def generate_author_biography(
        self, 
        author_name: str,
        language: str = "Turkish"
    ) -> Optional[str]:
        """
        Generate biographical information about an author.
        
        Args:
            author_name: Name of the author
            language: Response language (default: Turkish)
            
        Returns:
            Generated biography or None if API call fails
        """
        if not self.is_configured():
            logger.error("OpenAI service is not configured")
            return None
        
        try:
            prompt = f"""
            Provide a brief biography (2-3 paragraphs) of the author {author_name}.
            Language: {language}
            
            Include their major works and contributions to literature.
            """
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return message.content[0].text
            
        except AuthenticationError as e:
            logger.error(f"OpenAI Authentication Error: {e}")
            return None
        except RateLimitError as e:
            logger.error(f"OpenAI Rate Limit Error: {e}")
            return None
        except APIError as e:
            logger.error(f"OpenAI API Error: {e}")
            return None


# Singleton instance
_openai_service = None

def get_openai_service() -> OpenAIService:
    """Get or create OpenAI service singleton instance."""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
