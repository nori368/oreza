"""
Google Search Module for Oreza v1
Wrapper for Google Custom Search API
"""

import httpx
import logging
import os

logger = logging.getLogger("google_search")

class GoogleSearch:
    """Google Custom Search API wrapper"""
    
    def __init__(self):
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.cx = os.getenv("GOOGLE_CSE_ID")
        
        if not self.api_key or not self.cx:
            logger.warning("Google Search API credentials not found. Using mock mode.")
            self.mock_mode = True
        else:
            logger.info("GoogleSearch initialized with API credentials")
            self.mock_mode = False
    
    async def search(self, query: str, num: int = 5, search_type: str = "web") -> dict:
        """
        Perform a web or image search
        
        Args:
            query: Search query
            num: Number of results to return (max 10)
            search_type: "web" or "image"
            
        Returns:
            dict with 'results' key containing list of search results
        """
        try:
            # If API credentials are not available, use mock mode
            if self.mock_mode:
                logger.info(f"Mock search query: {query}, type: {search_type}, num: {num}")
                if search_type == "image":
                    return {
                        "results": [
                            {
                                "title": f"画像検索結果: {query}",
                                "image_url": "https://via.placeholder.com/300x200?text=Mock+Image",
                                "thumbnail": "https://via.placeholder.com/150x100?text=Mock+Thumb",
                                "link": "https://console.cloud.google.com/apis/credentials"
                            }
                        ],
                        "query": query,
                        "search_type": "image"
                    }
                else:
                    return {
                        "results": [
                            {
                                "title": f"検索結果: {query}",
                                "snippet": "Google Search APIの認証情報が設定されていません。環境変数 GOOGLE_API_KEY と GOOGLE_SEARCH_CX を設定してください。",
                                "link": "https://console.cloud.google.com/apis/credentials"
                            }
                        ],
                        "query": query,
                        "search_type": "web"
                    }
            
            # Perform actual Google Custom Search
            logger.info(f"Google Search query: {query}, type: {search_type}, num: {num}")
            
            params = {
                "key": self.api_key,
                "cx": self.cx,
                "q": query,
                "num": min(num, 10),  # Google API max is 10
                "lr": "lang_ja",  # Language restrict to Japanese
                "hl": "ja",  # Interface language
                "gl": "jp"  # Geolocation (Japan)
            }
            
            # Add searchType for image search
            if search_type == "image":
                params["searchType"] = "image"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.base_url,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse search results
                    results = []
                    if "items" in data:
                        for item in data["items"]:
                            if search_type == "image":
                                # Image search results
                                image_data = item.get("image", {})
                                results.append({
                                    "title": item.get("title", ""),
                                    "image_url": item.get("link", ""),
                                    "thumbnail": image_data.get("thumbnailLink", ""),
                                    "context_link": image_data.get("contextLink", ""),
                                    "width": image_data.get("width", 0),
                                    "height": image_data.get("height", 0)
                                })
                            else:
                                # Web search results
                                results.append({
                                    "title": item.get("title", ""),
                                    "snippet": item.get("snippet", ""),
                                    "link": item.get("link", "")
                                })
                    
                    logger.info(f"Found {len(results)} {search_type} search results")
                    
                    # Sort results by priority for web search
                    if search_type == "web" and results:
                        results = self._sort_results_by_priority(results)
                    
                    return {
                        "results": results,
                        "query": query,
                        "search_type": search_type
                    }
                else:
                    logger.error(f"Google Search API error: {response.status_code}")
                    return {
                        "results": [{
                            "title": "検索エラー",
                            "snippet": f"Google Search APIがエラーを返しました (HTTP {response.status_code})",
                            "link": ""
                        }],
                        "error": f"HTTP {response.status_code}"
                    }
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {
                "results": [{
                    "title": "検索エラー",
                    "snippet": f"検索中にエラーが発生しました: {str(e)}",
                    "link": ""
                }],
                "error": str(e)
            }
    
    def _sort_results_by_priority(self, results: list) -> list:
        """
        Sort search results by priority:
        1. YouTube official
        2. Official sites (Instagram, Facebook, Twitter, etc.)
        3. Subscription services (Spotify, Apple Music, etc.)
        4. LINE MUSIC and similar services
        5. Shops and others
        """
        def get_priority(result):
            url = result.get('link', '').lower()
            title = result.get('title', '').lower()
            
            # Priority 1: YouTube official
            if 'youtube.com' in url or 'youtu.be' in url:
                return 1
            
            # Priority 2: Official sites (social media, official websites)
            official_domains = [
                'instagram.com', 'facebook.com', 'twitter.com', 'x.com',
                'tiktok.com'
            ]
            if any(domain in url for domain in official_domains):
                return 2
            
            # Also check for official in title
            if '公式' in title or 'official' in title:
                return 2
            
            # Priority 3: Major subscription services
            major_subscription_services = [
                'spotify.com', 'music.apple.com', 'music.amazon.',
                'music.youtube.com', 'soundcloud.com'
            ]
            if any(service in url for service in major_subscription_services):
                return 3
            
            # Priority 4: LINE MUSIC and similar services
            other_music_services = [
                'music.line.me', 'tidal.com', 'deezer.com', 'kkbox.com',
                'mora.jp', 'recochoku.jp'
            ]
            if any(service in url for service in other_music_services):
                return 4
            
            # Priority 5: Shops and others
            return 5
        
        # Sort by priority
        sorted_results = sorted(results, key=get_priority)
        return sorted_results
