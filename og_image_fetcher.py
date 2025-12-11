"""
Open Graph Image Fetcher
Fetches OG images from URLs for tab previews
"""
import httpx
from bs4 import BeautifulSoup
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class OGImageFetcher:
    def __init__(self):
        self.timeout = 10.0
        
    async def fetch_og_image(self, url: str) -> Optional[str]:
        """
        Fetch Open Graph image URL from a webpage
        
        Args:
            url: The URL to fetch OG image from
            
        Returns:
            OG image URL or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {url}: {response.status_code}")
                    return None
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try to find og:image meta tag
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    image_url = og_image['content']
                    # Handle relative URLs
                    if image_url.startswith('//'):
                        image_url = 'https:' + image_url
                    elif image_url.startswith('/'):
                        from urllib.parse import urljoin
                        image_url = urljoin(url, image_url)
                    return image_url
                
                # Try twitter:image as fallback
                twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
                if twitter_image and twitter_image.get('content'):
                    image_url = twitter_image['content']
                    if image_url.startswith('//'):
                        image_url = 'https:' + image_url
                    elif image_url.startswith('/'):
                        from urllib.parse import urljoin
                        image_url = urljoin(url, image_url)
                    return image_url
                
                logger.info(f"No OG image found for {url}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching OG image from {url}: {e}")
            return None
