from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from app.config import get_settings
from app.services.base import BaseService

settings = get_settings()


class SearchService(BaseService):
    """Service for web search functionality"""
    
    def __init__(self):
        self.enabled = settings.GOOGLE_SEARCH_ENABLED
        self.max_results = settings.GOOGLE_MAX_RESULTS
    
    async def initialize(self) -> bool:
        """Initialize search service"""
        return True
    
    async def health_check(self) -> bool:
        """Check if search service is healthy"""
        return self.enabled
    
    def search_web(self, query: str, num_results: int = None) -> List[Dict[str, str]]:
        """
        Search the web using Google and return results
        
        Args:
            query: Search query
            num_results: Number of results to return (default from settings)
        
        Returns:
            List of dictionaries with 'title', 'url', 'snippet'
        """
        if not self.enabled:
            return []
        
        if num_results is None:
            num_results = self.max_results
        
        results = []
        
        try:
            # Perform Google search
            search_results = search(query, num_results=num_results, lang="ru", advanced=True)
            
            for result in search_results:
                results.append({
                    'title': result.title or 'Без названия',
                    'url': result.url,
                    'snippet': result.description or ''
                })
            
        except Exception as e:
            print(f"Error performing web search: {e}")
        
        return results
    
    def get_page_content(self, url: str, max_length: int = 1000) -> Optional[str]:
        """
        Fetch and extract main content from a web page
        
        Args:
            url: URL to fetch
            max_length: Maximum length of content to return
        
        Returns:
            Extracted text content or None if failed
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Truncate if needed
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            return text
            
        except Exception as e:
            print(f"Error fetching page content from {url}: {e}")
            return None
    
    def format_search_results(self, results: List[Dict[str, str]]) -> str:
        """
        Format search results for LLM context
        
        Args:
            results: List of search result dictionaries
        
        Returns:
            Formatted string with search results
        """
        if not results:
            return ""
        
        formatted = "🔍 РЕЗУЛЬТАТЫ ПОИСКА В ИНТЕРНЕТЕ:\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"   URL: {result['url']}\n"
            if result['snippet']:
                formatted += f"   {result['snippet']}\n"
            formatted += "\n"
        
        return formatted


# Singleton instance
search_service = SearchService()
