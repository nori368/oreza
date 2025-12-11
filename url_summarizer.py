"""
URL Summarizer Module for Oreza v1
Fetches URL content and provides AI-powered summary with safety check
"""

import httpx
import logging
from bs4 import BeautifulSoup
from typing import Dict, Optional

logger = logging.getLogger("url_summarizer")

class URLSummarizer:
    """URL content fetcher and summarizer"""
    
    def __init__(self):
        self.timeout = 10.0
        self.max_content_length = 5000  # Limit content for AI processing
    
    async def fetch_content(self, url: str) -> Optional[str]:
        """Fetch and extract text content from URL"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; OrezaBot/1.0)'
                })
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch URL: {url}, status: {response.status_code}")
                    return None
                
                # Parse HTML content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text()
                
                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                # Limit content length
                if len(text) > self.max_content_length:
                    text = text[:self.max_content_length] + "..."
                
                logger.info(f"Successfully fetched content from {url}, length: {len(text)}")
                return text
                
        except Exception as e:
            logger.error(f"Error fetching URL {url}: {e}")
            return None
    
    async def summarize_url(self, url: str) -> Dict:
        """
        Fetch URL content and generate AI summary with safety check
        
        Returns:
            dict with 'summary', 'safety', 'title' keys
        """
        try:
            # Fetch content
            content = await self.fetch_content(url)
            
            if not content:
                return {
                    "summary": "URLのコンテンツを取得できませんでした。",
                    "safety": "unknown",
                    "error": "fetch_failed"
                }
            
            # Use OpenAI API for summarization
            from openai import OpenAI
            client = OpenAI()
            
            prompt = f"""以下のWebページの内容を要約し、安全性を評価してください。

URL: {url}

コンテンツ:
{content[:3000]}

以下の形式でJSON形式で返してください:
{{
  "title": "ページのタイトル",
  "summary": "2-3文での要約",
  "safety": "safe/caution/danger",
  "safety_note": "安全性に関する簡単なコメント(危険な場合のみ)"
}}

safety判定基準:
- safe: 一般的な情報サイト、公式サイト、ニュースサイトなど
- caution: 広告が多い、不明なサイト、個人情報入力が必要そうなサイト
- danger: フィッシング、マルウェア、詐欺の可能性があるサイト
"""
            
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content
            
            # Extract JSON from response
            import re
            import json
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                logger.info(f"URL summary generated for {url}: {result.get('safety', 'unknown')}")
                return result
            else:
                logger.warning(f"Failed to parse JSON from AI response")
                return {
                    "summary": result_text,
                    "safety": "unknown"
                }
                
        except Exception as e:
            logger.error(f"Error summarizing URL {url}: {e}")
            return {
                "summary": f"要約中にエラーが発生しました: {str(e)}",
                "safety": "unknown",
                "error": str(e)
            }
