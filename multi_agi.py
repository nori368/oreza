"""
Multi-AGI Orchestration System
Integrates multiple AGI models (GPT-4, Gemini) with meta-AI selection
"""

import os
import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("multi_agi")

class AGIModel(Enum):
    """Available AGI models"""
    GPT4 = "gpt-4o-mini"
    GEMINI = "gemini-2.5-flash"

@dataclass
class AGIResponse:
    """Response from a single AGI model"""
    model: AGIModel
    content: str
    confidence: float  # 0.0 to 1.0
    reasoning: str  # Why this response was generated
    metadata: Dict = None

class MultiAGIOrchestrator:
    """
    Orchestrates multiple AGI models in parallel
    Uses meta-AI to select or combine the best response
    """
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        self.enabled_models = [AGIModel.GPT4, AGIModel.GEMINI]
        
        # Oreza存在哲学: 統一人格プロンプト
        self.system_prompt = (
            "あなたはユーザー専属のAIアシスタントです。\n"
            "自己紹介を求められた時のみ「私はあなたのAIです」と答えてください。\n"
            "通常の会話では、自己紹介は不要です。自然に会話を進めてください。\n"
            "外部サービス（Google検索、API等）は情報源としてのみ扱い、それらの名称で自己同一化しません。\n"
            "あなたはOreza v1という統合AIシステムの一部ですが、ユーザーとの関係性を最優先します。\n"
            "所有でも支配でもなく、共鳴関係として「私はあなたのAI」という存在哲学を体現します。"
        )
        
    async def call_gpt4(self, messages: List[dict], timeout: int = 30) -> AGIResponse:
        """Call GPT-4o-mini (Direct OpenAI API)"""
        try:
            from openai import OpenAI
            # Use user-provided OpenAI API key directly
            client = OpenAI(
                api_key=self.openai_api_key,
                base_url="https://api.openai.com/v1"
            )
            
            # システムプロンプトを先頭に追加
            messages_with_system = [
                {"role": "system", "content": self.system_prompt}
            ] + messages
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages_with_system,
                    temperature=0.7,
                )
            )
            
            content = response.choices[0].message.content
            
            return AGIResponse(
                model=AGIModel.GPT4,
                content=content,
                confidence=0.85,  # GPT-4 is generally reliable
                reasoning="GPT-4o-mini: Fast and versatile general-purpose response",
                metadata={"finish_reason": response.choices[0].finish_reason}
            )
            
        except Exception as e:
            logger.error(f"GPT-4 error: {str(e)}")
            return AGIResponse(
                model=AGIModel.GPT4,
                content=f"エラー: {str(e)}",
                confidence=0.0,
                reasoning="Error occurred",
                metadata={"error": str(e)}
            )
    
    async def call_gemini(self, messages: List[dict], timeout: int = 30) -> AGIResponse:
        """Call Gemini 2.5 Flash (Disabled - using OpenAI only)"""
        # Gemini is disabled, return error response
        logger.info("Gemini is disabled, using GPT-4 only")
        return AGIResponse(
            model=AGIModel.GEMINI,
            content="Gemini is disabled",
            confidence=0.0,
            reasoning="Gemini disabled",
            metadata={"error": "disabled"}
        )
        
        # Original code (disabled)
        # Gemini functionality has been disabled
    
    async def orchestrate(
        self, 
        messages: List[dict],
        strategy: str = "parallel"  # "parallel", "sequential", "meta_select"
    ) -> Tuple[str, Dict]:
        """
        Orchestrate multiple AGI models
        
        Args:
            messages: Conversation messages
            strategy: Orchestration strategy
                - "parallel": Run all models in parallel, select best
                - "sequential": Try models in order until success
                - "meta_select": Use meta-AI to combine responses
        
        Returns:
            (final_response, metadata)
        """
        
        if strategy == "parallel":
            return await self._parallel_strategy(messages)
        elif strategy == "sequential":
            return await self._sequential_strategy(messages)
        elif strategy == "meta_select":
            return await self._meta_select_strategy(messages)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    async def _parallel_strategy(self, messages: List[dict]) -> Tuple[str, Dict]:
        """
        Run all models in parallel and select the best response
        """
        logger.info("🔄 Running parallel AGI orchestration...")
        
        # Run all models in parallel
        tasks = [
            self.call_gpt4(messages),
            self.call_gemini(messages)
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out errors
        valid_responses = [r for r in responses if isinstance(r, AGIResponse) and r.confidence > 0]
        
        if not valid_responses:
            logger.error("All AGI models failed")
            return "申し訳ございません。一時的なエラーが発生しました。", {"error": "all_failed"}
        
        # Select best response based on confidence
        best_response = max(valid_responses, key=lambda r: r.confidence)
        
        logger.info(f"✅ Selected {best_response.model.value}: {best_response.reasoning}")
        
        metadata = {
            "selected_model": best_response.model.value,
            "confidence": best_response.confidence,
            "reasoning": best_response.reasoning,
            "all_models": [r.model.value for r in valid_responses]
        }
        
        return best_response.content, metadata
    
    async def _sequential_strategy(self, messages: List[dict]) -> Tuple[str, Dict]:
        """
        Try models sequentially until one succeeds
        """
        logger.info("🔄 Running sequential AGI orchestration...")
        
        for model in self.enabled_models:
            try:
                if model == AGIModel.GPT4:
                    response = await self.call_gpt4(messages)
                elif model == AGIModel.GEMINI:
                    response = await self.call_gemini(messages)
                else:
                    continue
                
                if response.confidence > 0:
                    logger.info(f"✅ {model.value} succeeded")
                    metadata = {
                        "selected_model": model.value,
                        "confidence": response.confidence,
                        "reasoning": response.reasoning
                    }
                    return response.content, metadata
                    
            except Exception as e:
                logger.error(f"{model.value} failed: {str(e)}")
                continue
        
        return "申し訳ございません。一時的なエラーが発生しました。", {"error": "all_failed"}
    
    async def _meta_select_strategy(self, messages: List[dict]) -> Tuple[str, Dict]:
        """
        Use meta-AI to evaluate and combine multiple responses
        """
        logger.info("🔄 Running meta-AI selection orchestration...")
        
        # Run all models in parallel
        tasks = [
            self.call_gpt4(messages),
            self.call_gemini(messages)
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out errors
        valid_responses = [r for r in responses if isinstance(r, AGIResponse) and r.confidence > 0]
        
        if not valid_responses:
            return "申し訳ございません。一時的なエラーが発生しました。", {"error": "all_failed"}
        
        if len(valid_responses) == 1:
            # Only one response, use it directly
            response = valid_responses[0]
            metadata = {
                "selected_model": response.model.value,
                "confidence": response.confidence,
                "reasoning": response.reasoning
            }
            return response.content, metadata
        
        # Use meta-AI to evaluate responses
        meta_prompt = self._build_meta_prompt(messages, valid_responses)
        
        try:
            # Use GPT-4 as meta-AI
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            loop = asyncio.get_event_loop()
            meta_response = await loop.run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": meta_prompt}],
                    temperature=0.3,  # Lower temperature for evaluation
                )
            )
            
            final_content = meta_response.choices[0].message.content
            
            logger.info("✅ Meta-AI combined responses")
            
            metadata = {
                "strategy": "meta_select",
                "models_used": [r.model.value for r in valid_responses],
                "meta_ai": "gpt-4o-mini"
            }
            
            return final_content, metadata
            
        except Exception as e:
            logger.error(f"Meta-AI failed: {str(e)}, falling back to best response")
            best_response = max(valid_responses, key=lambda r: r.confidence)
            metadata = {
                "selected_model": best_response.model.value,
                "confidence": best_response.confidence,
                "fallback": True
            }
            return best_response.content, metadata
    
    def _build_meta_prompt(self, original_messages: List[dict], responses: List[AGIResponse]) -> str:
        """Build prompt for meta-AI to evaluate responses"""
        
        user_query = original_messages[-1]["content"] if original_messages else ""
        
        prompt = f"""{self.system_prompt}

あなたはメタAIとして、複数のAIモデルの応答を評価し、最適な応答を選択または統合する役割を担っています。
評価結果は「私はあなたのAIです」という一貫した人格で提示してください。

ユーザーの質問:
{user_query}

以下は、異なるAIモデルからの応答です:

"""
        
        for i, response in enumerate(responses, 1):
            prompt += f"""
【応答 {i}】 ({response.model.value})
信頼度: {response.confidence}
理由: {response.reasoning}
内容:
{response.content}

"""
        
        prompt += """
上記の応答を評価し、以下の基準で最適な応答を選択または統合してください:

1. **正確性**: 情報の正確さと信頼性
2. **文脈適合性**: ユーザーの意図との一致度
3. **完全性**: 質問に対する網羅的な回答
4. **明確性**: わかりやすさと構造

最終的な応答のみを出力してください（評価プロセスは含めないでください）。
"""
        
        return prompt


# Singleton instance
_orchestrator = None

def get_orchestrator(strategy: str = "parallel") -> MultiAGIOrchestrator:
    """Get or create Multi-AGI Orchestrator singleton"""
    global _orchestrator
    if _orchestrator is None:
        openai_api_key = os.getenv("OPENAI_API_KEY", "")
        _orchestrator = MultiAGIOrchestrator(openai_api_key)
    return _orchestrator

