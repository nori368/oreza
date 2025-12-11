"""
AI Auto Search Module
AIが自動的に検索が必要か判断し、Google検索を実行して学習する機能
"""
import logging
from openai import OpenAI
import os
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger("ai_auto_search")

class AIAutoSearch:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    async def should_search(self, user_message: str) -> dict:
        """
        ユーザーのメッセージから検索が必要か判断し、検索クエリを生成
        
        Returns:
            {
                "should_search": bool,
                "query": str  # 検索クエリ
            }
        """
        try:
            prompt = f"""あなたは検索が必要かどうかを判断するAIアシスタントです。

ユーザーの質問を分析して、Google検索が必要かどうかを判断してください。

検索が必要な場合:
- 最新の情報が必要な質問(ニュース、天気、株価、イベントなど)
- 事実確認が必要な質問(歴史、統計、データなど)
- 具体的な情報を求める質問(営業時間、場所、価格など)
- 専門的な知識が必要な質問
- あなたの知識では答えられない質問

検索が不要な場合:
- 一般的な会話や挨拶
- 個人的な意見や感想を求める質問
- 簡単な計算や論理的推論で答えられる質問
- 一般常識で答えられる質問

ユーザーメッセージ: {user_message}

以下のJSON形式で回答してください:
{{
    "should_search": true/false,
    "query": "検索クエリ(検索が必要な場合のみ、日本語で簡潔に)"
}}"""

            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Search decision: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in should_search: {e}")
            return {"should_search": False, "query": ""}
    
    async def fetch_page_content(self, url: str) -> str:
        """
        URLからページ内容を取得してテキスト化
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up text
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            clean_text = '\n'.join(lines)
            
            # Limit to first 3000 characters
            if len(clean_text) > 3000:
                clean_text = clean_text[:3000] + "..."
            
            return clean_text
            
        except Exception as e:
            logger.error(f"Error fetching page content from {url}: {e}")
            return ""
    
    async def generate_answer_with_search(self, user_message: str, search_query: str, page_content: str, page_url: str) -> str:
        """
        検索結果のページ内容を学習してAIが回答を生成
        
        Args:
            user_message: ユーザーのメッセージ
            search_query: 検索クエリ
            page_content: 取得したページの内容
            page_url: ページのURL
            
        Returns:
            str: 生成された回答
        """
        try:
            prompt = f"""あなたは親切で知識豊富なAIアシスタント「Oreza」です。

ユーザーの質問に対して、Webページから取得した情報を学習して回答を生成してください。

ユーザーの質問: {user_message}

検索クエリ: {search_query}

取得した情報(URL: {page_url}):
{page_content}

回答のガイドライン:
1. 取得した情報を基に、正確で分かりやすい回答を生成
2. 情報源のURLを最後に記載する
3. 取得した情報に答えがない場合は、その旨を伝える
4. 日本語で自然な会話口調で回答
5. 必要に応じて箇条書きや段落を使って読みやすく
6. 回答は簡潔に(300文字程度)

回答:"""

            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400
            )
            
            answer = response.choices[0].message.content
            
            # Add source URL
            answer += f"\n\n📎 参考: {page_url}"
            
            logger.info(f"Generated answer from page content")
            return answer
            
        except Exception as e:
            logger.error(f"Error in generate_answer_with_search: {e}")
            return "申し訳ございません。検索結果から回答を生成できませんでした。"
