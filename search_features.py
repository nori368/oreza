"""
Search Features: Favorites and History
Provides bookmark and history management for search results
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel

class SearchHistoryItem(BaseModel):
    query: str
    timestamp: str
    results_count: int
    
class SearchFavoriteItem(BaseModel):
    title: str
    url: str
    snippet: str
    added_at: str
    tags: List[str] = []

class SearchFeaturesManager:
    """Manages search history and favorites"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.history_file = os.path.join(data_dir, "search_history.json")
        self.favorites_file = os.path.join(data_dir, "search_favorites.json")
        
    def _load_json(self, filepath: str) -> List[Dict]:
        """Load JSON file"""
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _save_json(self, filepath: str, data: List[Dict]):
        """Save JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ========== History Management ==========
    
    def add_history(self, query: str, results_count: int) -> bool:
        """Add search query to history"""
        history = self._load_json(self.history_file)
        
        # Add new entry
        entry = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results_count": results_count
        }
        
        # Remove duplicates (keep latest)
        history = [h for h in history if h.get("query") != query]
        history.insert(0, entry)
        
        # Keep only last 100 entries
        history = history[:100]
        
        self._save_json(self.history_file, history)
        return True
    
    def get_history(self, limit: int = 50) -> List[SearchHistoryItem]:
        """Get search history"""
        history = self._load_json(self.history_file)
        return [SearchHistoryItem(**h) for h in history[:limit]]
    
    def clear_history(self) -> bool:
        """Clear all search history"""
        self._save_json(self.history_file, [])
        return True
    
    def delete_history_item(self, query: str) -> bool:
        """Delete specific history item"""
        history = self._load_json(self.history_file)
        history = [h for h in history if h.get("query") != query]
        self._save_json(self.history_file, history)
        return True
    
    # ========== Favorites Management ==========
    
    def add_favorite(self, title: str, url: str, snippet: str = "", tags: List[str] = None) -> bool:
        """Add search result to favorites"""
        favorites = self._load_json(self.favorites_file)
        
        # Check if already exists
        if any(f.get("url") == url for f in favorites):
            return False
        
        # Add new favorite
        entry = {
            "title": title,
            "url": url,
            "snippet": snippet,
            "added_at": datetime.now().isoformat(),
            "tags": tags or []
        }
        
        favorites.insert(0, entry)
        self._save_json(self.favorites_file, favorites)
        return True
    
    def get_favorites(self, tag: Optional[str] = None) -> List[SearchFavoriteItem]:
        """Get all favorites, optionally filtered by tag"""
        favorites = self._load_json(self.favorites_file)
        
        if tag:
            favorites = [f for f in favorites if tag in f.get("tags", [])]
        
        return [SearchFavoriteItem(**f) for f in favorites]
    
    def delete_favorite(self, url: str) -> bool:
        """Delete favorite by URL"""
        favorites = self._load_json(self.favorites_file)
        favorites = [f for f in favorites if f.get("url") != url]
        self._save_json(self.favorites_file, favorites)
        return True
    
    def update_favorite_tags(self, url: str, tags: List[str]) -> bool:
        """Update tags for a favorite"""
        favorites = self._load_json(self.favorites_file)
        
        for f in favorites:
            if f.get("url") == url:
                f["tags"] = tags
                self._save_json(self.favorites_file, favorites)
                return True
        
        return False
    
    def search_favorites(self, keyword: str) -> List[SearchFavoriteItem]:
        """Search favorites by keyword"""
        favorites = self._load_json(self.favorites_file)
        keyword_lower = keyword.lower()
        
        results = [
            f for f in favorites
            if keyword_lower in f.get("title", "").lower()
            or keyword_lower in f.get("snippet", "").lower()
            or keyword_lower in f.get("url", "").lower()
        ]
        
        return [SearchFavoriteItem(**f) for f in results]
