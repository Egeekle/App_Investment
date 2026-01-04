"""
News Client for fetching financial news
"""
import requests
import logging
from typing import List, Dict, Any
import xml.etree.ElementTree as ET
from datetime import datetime

logger = logging.getLogger(__name__)

class NewsClient:
    """Client for fetching financial news from RSS feeds"""
    
    RSS_FEEDS = {
        "general": "https://finance.yahoo.com/news/rssindex",
        "crypto": "https://cointelegraph.com/rss"
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def get_news(self, category: str = "general", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch news from RSS feed
        
        Args:
            category: 'general' or 'crypto'
            limit: Max number of news items
            
        Returns:
            List of news dictionaries containing title, link, pubDate, summary
        """
        url = self.RSS_FEEDS.get(category, self.RSS_FEEDS["general"])
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Simple XML parsing
            root = ET.fromstring(response.content)
            
            items = []
            for item in root.findall(".//item")[:limit]:
                title = item.find("title").text if item.find("title") is not None else "No Title"
                link = item.find("link").text if item.find("link") is not None else ""
                pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                description = item.find("description").text if item.find("description") is not None else ""
                
                # Check for CoinTelegraph content which might be in content:encoded?
                # For now stick to description
                
                news_item = {
                    "title": title,
                    "link": link,
                    "published_at": pub_date,
                    "summary": description,
                    "source": category,
                    "fetched_at": datetime.now().isoformat()
                }
                items.append(news_item)
                
            logger.info(f"Fetched {len(items)} news items from {category}")
            return items
            
        except Exception as e:
            logger.error(f"Error fetching news from {url}: {e}")
            return []

    def process_and_structure_for_rag(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert news items to RAG-ready format (text chunk + metadata)
        """
        rag_docs = []
        for item in news_items:
            # Create a rich text representation
            text_content = f"Title: {item['title']}\nDate: {item['published_at']}\nSource: {item['source']}\nSummary: {item['summary']}"
            
            rag_docs.append({
                "page_content": text_content,
                "metadata": {
                    "title": item['title'],
                    "source": item['source'],
                    "url": item['link'],
                    "type": "news"
                }
            })
        return rag_docs
