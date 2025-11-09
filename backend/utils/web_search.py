"""
Web search utilities for external knowledge retrieval
"""
from typing import List, Dict, Any, Optional
import httpx
from duckduckgo_search import DDGS
from backend.config import settings

class WebSearcher:
    """Web search functionality using DuckDuckGo"""
    
    def __init__(self):
        """Initialize web searcher"""
        self.ddgs = DDGS()
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        region: str = "wt-wt"
    ) -> List[Dict[str, Any]]:
        """
        Perform web search
        
        Args:
            query: Search query
            max_results: Maximum number of results
            region: Search region
            
        Returns:
            List of search results
        """
        try:
            results = []
            search_results = self.ddgs.text(query, region=region, max_results=max_results)
            
            for result in search_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                })
            
            return results
        except Exception as e:
            print(f"Web search error: {str(e)}")
            return []
    
    def get_instant_answer(self, query: str) -> Optional[str]:
        """
        Get instant answer for a query
        
        Args:
            query: Search query
            
        Returns:
            Instant answer or None
        """
        try:
            results = self.ddgs.answers(query)
            if results:
                return results[0].get("text", "")
            return None
        except Exception as e:
            print(f"Instant answer error: {str(e)}")
            return None
    
    def search_news(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for news articles
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of news results
        """
        try:
            results = []
            news_results = self.ddgs.news(query, max_results=max_results)
            
            for result in news_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("body", ""),
                    "date": result.get("date", ""),
                    "source": result.get("source", "")
                })
            
            return results
        except Exception as e:
            print(f"News search error: {str(e)}")
            return []

# Global web searcher instance
web_searcher = WebSearcher()

def web_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Convenience function for web search
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        List of search results
    """
    if not settings.ENABLE_WEB_SEARCH:
        return []
    
    return web_searcher.search(query, max_results)
