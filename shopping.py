"""
Oreza Shopping Module
AI-powered shopping assistant with product search and recommendations
"""

import os
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from google_search import GoogleSearch

logger = logging.getLogger("oreza_shopping")

@dataclass
class ProductCard:
    """Product information card"""
    title: str
    price: str
    image_url: str
    product_url: str
    rating: Optional[float] = None
    review_count: Optional[int] = None
    delivery_info: Optional[str] = None
    stock_status: Optional[str] = None
    ai_summary: Optional[Dict] = None  # AI-generated summary
    
class AIShoppingSommelier:
    """
    AI Shopping Sommelier
    Provides intelligent product recommendations and analysis
    """
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.search = GoogleSearch()
        
    async def search_products(self, query: str, num: int = 10) -> List[ProductCard]:
        """
        Search for products using Google Custom Search
        
        Args:
            query: Search query (e.g., "ワンピース レディース")
            num: Number of results to return
            
        Returns:
            List of ProductCard objects
        """
        try:
            # Perform Google search
            results = await self.search.search(query, num=num)
            
            products = []
            for item in results.get('results', []):
                # Extract product information from search results
                product = ProductCard(
                    title=item.get('title', ''),
                    price=self._extract_price(item),
                    image_url=item.get('image', ''),
                    product_url=item.get('link', ''),
                    rating=None,  # Will be extracted from page metadata
                    review_count=None,
                    delivery_info=None,
                    stock_status=None,
                    ai_summary=None
                )
                products.append(product)
            
            logger.info(f"Found {len(products)} products for query: {query}")
            return products
            
        except Exception as e:
            logger.error(f"Product search error: {e}")
            return []
    
    def _extract_price(self, item: Dict) -> str:
        """Extract price from search result"""
        snippet = item.get('snippet', '')
        title = item.get('title', '')
        
        # Look for price patterns (¥1,000, ¥2,980, etc.)
        import re
        price_pattern = r'¥[\d,]+'
        
        # Try snippet first
        match = re.search(price_pattern, snippet)
        if match:
            return match.group(0)
        
        # Try title
        match = re.search(price_pattern, title)
        if match:
            return match.group(0)
        
        return "価格不明"
    
    async def analyze_product(self, product: ProductCard, user_context: Optional[str] = None) -> Dict:
        """
        AI analysis of a product
        
        Args:
            product: ProductCard object
            user_context: Optional user context (e.g., "30代女性、カジュアル好き")
            
        Returns:
            AI-generated analysis with strengths, silhouette, cautions, etc.
        """
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=self.openai_api_key,
                base_url="https://api.openai.com/v1"
            )
            
            # Prepare prompt for AI analysis
            prompt = f"""
以下の商品について、AIソムリエとして分析してください。

【商品情報】
タイトル: {product.title}
価格: {product.price}
URL: {product.product_url}

【ユーザー情報】
{user_context or "一般ユーザー"}

【分析項目】
1. 強み（3点以内）
2. シルエット・デザイン
3. 注意点
4. 向いている人
5. 向いていない人

JSON形式で返してください：
{{
  "strengths": ["強み1", "強み2", "強み3"],
  "silhouette": "シルエットの説明",
  "cautions": "注意点",
  "suitable_for": "向いている人",
  "not_suitable_for": "向いていない人",
  "one_line_summary": "一言で商品を表現"
}}
"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "あなたは商品分析のプロフェッショナルなAIソムリエです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content)
            
            logger.info(f"AI analysis completed for: {product.title}")
            return analysis
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return {
                "strengths": ["分析中にエラーが発生しました"],
                "silhouette": "",
                "cautions": "",
                "suitable_for": "",
                "not_suitable_for": "",
                "one_line_summary": ""
            }
    
    async def analyze_fashion_fit(self, product: ProductCard, user_profile: Dict) -> Dict:
        """
        Fashion-specific analysis (size, material, fit)
        
        Args:
            product: ProductCard object
            user_profile: User profile with body type, preferences, etc.
            
        Returns:
            Fashion-specific analysis
        """
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=self.openai_api_key,
                base_url="https://api.openai.com/v1"
            )
            
            prompt = f"""
以下のファッション商品について、サイズ・素材・フィット感を分析してください。

【商品情報】
タイトル: {product.title}
価格: {product.price}

【ユーザープロファイル】
体型: {user_profile.get('body_type', '標準')}
好みのスタイル: {user_profile.get('style_preference', 'カジュアル')}
サイズの悩み: {user_profile.get('size_concerns', 'なし')}

【分析項目】
1. 素材感（薄手/透け感/ストレッチ性）
2. サイズ選びガイド
3. 体型との相性
4. シーン別の着こなし提案

JSON形式で返してください：
{{
  "material": {{
    "thickness": "薄手/普通/厚手",
    "transparency": "透け感あり/なし",
    "stretch": "ストレッチあり/なし"
  }},
  "size_guide": "サイズ選びのアドバイス",
  "body_compatibility": "体型との相性",
  "styling_tips": ["着こなし提案1", "着こなし提案2"]
}}
"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "あなたはファッションコンサルタントです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content)
            
            logger.info(f"Fashion fit analysis completed for: {product.title}")
            return analysis
            
        except Exception as e:
            logger.error(f"Fashion fit analysis error: {e}")
            return {
                "material": {
                    "thickness": "不明",
                    "transparency": "不明",
                    "stretch": "不明"
                },
                "size_guide": "分析中にエラーが発生しました",
                "body_compatibility": "",
                "styling_tips": []
            }
    
    async def compare_products(self, products: List[ProductCard]) -> Dict:
        """
        Compare multiple products and provide recommendation
        
        Args:
            products: List of ProductCard objects
            
        Returns:
            Comparison analysis with recommendation
        """
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=self.openai_api_key,
                base_url="https://api.openai.com/v1"
            )
            
            # Prepare product list for comparison
            product_list = "\n".join([
                f"{i+1}. {p.title} - {p.price}"
                for i, p in enumerate(products[:5])  # Compare up to 5 products
            ])
            
            prompt = f"""
以下の商品を比較して、最もおすすめの商品を選んでください。

【商品リスト】
{product_list}

【比較基準】
- 価格
- 品質（タイトルから推測）
- コストパフォーマンス
- 汎用性

JSON形式で返してください：
{{
  "recommended_index": 0,
  "reason": "おすすめの理由",
  "comparison_summary": "比較のまとめ"
}}
"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "あなたは商品比較のエキスパートです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            
            import json
            comparison = json.loads(response.choices[0].message.content)
            
            logger.info(f"Product comparison completed for {len(products)} products")
            return comparison
            
        except Exception as e:
            logger.error(f"Product comparison error: {e}")
            return {
                "recommended_index": 0,
                "reason": "分析中にエラーが発生しました",
                "comparison_summary": ""
            }
