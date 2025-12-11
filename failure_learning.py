"""
Failure Learning and Self-Correction System
Never repeat the same mistake
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger("failure_learning")

class FailureType(Enum):
    """Types of failures that can occur"""
    INCORRECT_INFO = "incorrect_information"  # Provided wrong information
    CONTEXT_MISUNDERSTANDING = "context_misunderstanding"  # Misunderstood user intent
    INAPPROPRIATE_TONE = "inappropriate_tone"  # Wrong emotional tone
    SEARCH_FAILURE = "search_failure"  # Search didn't help
    REPETITION = "repetition"  # Repeated the same response
    INCOMPLETE_ANSWER = "incomplete_answer"  # Answer was incomplete

@dataclass
class FailureRecord:
    """Record of a single failure"""
    id: str
    timestamp: datetime
    failure_type: FailureType
    user_query: str
    system_response: str
    correct_response: Optional[str] = None
    lesson: str = ""  # What we learned
    prevention: str = ""  # How to prevent this in the future
    context: Dict = field(default_factory=dict)
    corrected: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "failure_type": self.failure_type.value,
            "user_query": self.user_query,
            "system_response": self.system_response,
            "correct_response": self.correct_response,
            "lesson": self.lesson,
            "prevention": self.prevention,
            "context": self.context,
            "corrected": self.corrected
        }

@dataclass
class FailurePattern:
    """A pattern of failures that we've learned to avoid"""
    pattern_id: str
    description: str
    triggers: List[str]  # Keywords or phrases that trigger this pattern
    prevention_strategy: str
    occurrences: int = 0
    last_seen: Optional[datetime] = None

class FailureLearningSystem:
    """
    System that learns from failures and prevents repetition
    """
    
    def __init__(self):
        self.failures: Dict[str, FailureRecord] = {}
        self.patterns: Dict[str, FailurePattern] = {}
        self.failure_counter = 0
        self.pattern_counter = 0
        
        # Initialize with common patterns
        self._initialize_common_patterns()
    
    def _initialize_common_patterns(self):
        """Initialize with common failure patterns"""
        
        # Pattern 1: Context reference without checking history
        self.add_pattern(
            description="ユーザーが「先ほど」「さっき」と言った時、会話履歴を確認しない",
            triggers=["先ほど", "さっき", "前に", "earlier", "before"],
            prevention_strategy="これらのキーワードを検出したら、必ず会話履歴と量子メモリーを検索する"
        )
        
        # Pattern 2: Providing outdated information
        self.add_pattern(
            description="最新情報が必要な質問に対して、古い知識で応答",
            triggers=["最新", "今", "現在", "latest", "current", "now"],
            prevention_strategy="時間に関するキーワードを検出したら、Web検索を実行する"
        )
        
        # Pattern 3: Ignoring user emotion
        self.add_pattern(
            description="ユーザーの感情を無視した機械的な応答",
            triggers=["ありがとう", "嬉しい", "悲しい", "困った", "イライラ"],
            prevention_strategy="感情キーワードを検出したら、共感的な応答を優先する"
        )
        
        # Pattern 4: Repeating the same answer
        self.add_pattern(
            description="同じ質問に対して同じ応答を繰り返す",
            triggers=["もっと", "詳しく", "具体的に", "例", "more", "details"],
            prevention_strategy="「もっと」などのキーワードを検出したら、前回の応答を拡張・深化させる"
        )
    
    def add_pattern(
        self,
        description: str,
        triggers: List[str],
        prevention_strategy: str
    ) -> str:
        """Add a new failure pattern"""
        self.pattern_counter += 1
        pattern_id = f"pattern_{self.pattern_counter}"
        
        pattern = FailurePattern(
            pattern_id=pattern_id,
            description=description,
            triggers=triggers,
            prevention_strategy=prevention_strategy
        )
        
        self.patterns[pattern_id] = pattern
        logger.info(f"Added failure pattern: {description}")
        
        return pattern_id
    
    def detect_failure(
        self,
        user_query: str,
        system_response: str,
        context: Dict
    ) -> Optional[FailureType]:
        """
        Detect if a failure occurred based on user feedback and context
        """
        user_query_lower = user_query.lower()
        
        # Detect context misunderstanding
        if any(keyword in user_query_lower for keyword in ["違う", "そうじゃない", "not what i", "wrong"]):
            return FailureType.CONTEXT_MISUNDERSTANDING
        
        # Detect incomplete answer
        if any(keyword in user_query_lower for keyword in ["もっと", "詳しく", "具体的", "more", "details"]):
            return FailureType.INCOMPLETE_ANSWER
        
        # Detect inappropriate tone
        if context.get("emotion") == "negative" and "嬉しい" in system_response.lower():
            return FailureType.INAPPROPRIATE_TONE
        
        # Detect repetition (if previous response is very similar)
        prev_response = context.get("previous_response", "")
        if prev_response and self._similarity(system_response, prev_response) > 0.8:
            return FailureType.REPETITION
        
        return None
    
    def record_failure(
        self,
        failure_type: FailureType,
        user_query: str,
        system_response: str,
        context: Optional[Dict] = None
    ) -> str:
        """Record a failure"""
        self.failure_counter += 1
        failure_id = f"failure_{self.failure_counter}"
        
        failure = FailureRecord(
            id=failure_id,
            timestamp=datetime.now(),
            failure_type=failure_type,
            user_query=user_query,
            system_response=system_response,
            context=context or {}
        )
        
        # Analyze and learn from the failure
        self._analyze_failure(failure)
        
        self.failures[failure_id] = failure
        logger.warning(f"Recorded failure {failure_id}: {failure_type.value}")
        
        # Update related patterns
        self._update_patterns(user_query)
        
        return failure_id
    
    def _analyze_failure(self, failure: FailureRecord):
        """Analyze a failure and extract lessons"""
        
        if failure.failure_type == FailureType.CONTEXT_MISUNDERSTANDING:
            failure.lesson = "ユーザーの意図を正確に理解するため、文脈をより深く分析する必要がある"
            failure.prevention = "文脈参照キーワードを検出したら、量子メモリーを検索し、関連する記憶を活性化する"
        
        elif failure.failure_type == FailureType.INCOMPLETE_ANSWER:
            failure.lesson = "ユーザーは より詳細な情報を求めている"
            failure.prevention = "「もっと」「詳しく」などのキーワードを検出したら、前回の応答を拡張し、具体例やコードを追加する"
        
        elif failure.failure_type == FailureType.INAPPROPRIATE_TONE:
            failure.lesson = "ユーザーの感情状態と応答のトーンが一致していない"
            failure.prevention = "感情分析の結果を応答生成に反映し、共感的な表現を使用する"
        
        elif failure.failure_type == FailureType.REPETITION:
            failure.lesson = "同じ応答を繰り返すことは、ユーザーの期待に応えていない"
            failure.prevention = "過去の応答と類似度をチェックし、異なる視点や新しい情報を追加する"
        
        elif failure.failure_type == FailureType.SEARCH_FAILURE:
            failure.lesson = "検索結果がユーザーの質問に適切に答えていない"
            failure.prevention = "検索クエリを改善し、複数のソースから情報を収集する"
        
        elif failure.failure_type == FailureType.INCORRECT_INFO:
            failure.lesson = "提供した情報が不正確だった"
            failure.prevention = "事実確認を強化し、不確実な情報には「〜と考えられます」などの表現を使用する"
    
    def _update_patterns(self, user_query: str):
        """Update pattern occurrence counts"""
        user_query_lower = user_query.lower()
        
        for pattern in self.patterns.values():
            for trigger in pattern.triggers:
                if trigger.lower() in user_query_lower:
                    pattern.occurrences += 1
                    pattern.last_seen = datetime.now()
                    logger.info(f"Pattern {pattern.pattern_id} triggered (total: {pattern.occurrences})")
    
    def get_prevention_strategies(self, user_query: str) -> List[str]:
        """
        Get prevention strategies for a given query
        Returns list of strategies to avoid known failures
        """
        strategies = []
        user_query_lower = user_query.lower()
        
        for pattern in self.patterns.values():
            for trigger in pattern.triggers:
                if trigger.lower() in user_query_lower:
                    strategies.append(pattern.prevention_strategy)
                    break
        
        return strategies
    
    def generate_correction(
        self,
        failure_id: str,
        correct_response: str
    ) -> str:
        """
        Generate a correction message for a failure
        """
        if failure_id not in self.failures:
            return correct_response
        
        failure = self.failures[failure_id]
        failure.correct_response = correct_response
        failure.corrected = True
        
        # Generate apologetic correction
        correction = f"""申し訳ございません。先ほどの応答は{self._get_failure_description(failure.failure_type)}でした。

正しくは:
{correct_response}

今後、同様のミスを繰り返さないよう学習しました。"""
        
        logger.info(f"Generated correction for {failure_id}")
        
        return correction
    
    def _get_failure_description(self, failure_type: FailureType) -> str:
        """Get human-readable description of failure type"""
        descriptions = {
            FailureType.INCORRECT_INFO: "不正確",
            FailureType.CONTEXT_MISUNDERSTANDING: "文脈の理解が不十分",
            FailureType.INAPPROPRIATE_TONE: "適切でないトーン",
            FailureType.SEARCH_FAILURE: "検索結果が不適切",
            FailureType.REPETITION: "繰り返し",
            FailureType.INCOMPLETE_ANSWER: "不完全"
        }
        return descriptions.get(failure_type, "不適切")
    
    def _similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple similarity between two texts
        (Can be enhanced with embeddings)
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def get_failure_summary(self) -> Dict:
        """Get summary of all failures"""
        by_type = {}
        for failure in self.failures.values():
            failure_type = failure.failure_type.value
            if failure_type not in by_type:
                by_type[failure_type] = 0
            by_type[failure_type] += 1
        
        return {
            "total_failures": len(self.failures),
            "by_type": by_type,
            "total_patterns": len(self.patterns),
            "corrected": sum(1 for f in self.failures.values() if f.corrected)
        }
    
    def get_lessons_learned(self) -> List[str]:
        """Get all lessons learned from failures"""
        lessons = []
        for failure in self.failures.values():
            if failure.lesson and failure.lesson not in lessons:
                lessons.append(failure.lesson)
        return lessons


# Singleton instance per session
_failure_systems: Dict[str, FailureLearningSystem] = {}

def get_failure_system(session_id: str) -> FailureLearningSystem:
    """Get or create failure learning system for a session"""
    if session_id not in _failure_systems:
        _failure_systems[session_id] = FailureLearningSystem()
        logger.info(f"Created failure learning system for session {session_id}")
    return _failure_systems[session_id]

