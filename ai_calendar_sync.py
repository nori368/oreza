"""
AIチャット ↔ カレンダー同期プロト
- インテント定義
- JSONスキーマ
- 自然文 → 予定JSON 変換（ユーザー指定仕様準拠）
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel
import os
from openai import OpenAI
import json
import re

# OpenAI APIクライアント（遅延初期化）
client = None

def get_openai_client():
    global client
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        client = OpenAI(api_key=api_key)
    return client

# ===== インテント定義 =====

INTENTS = [
    "CREATE_EVENT",      # イベント新規作成
    "UPDATE_EVENT",      # 既存イベントの編集
    "DELETE_EVENT",      # イベント削除
    "LIST_AGENDA",       # 今日/指定日の予定取得
    "CREATE_TASK",       # タスク作成
    "UPDATE_TASK",       # タスク編集
    "CANCEL_EVENT",      # 予約キャンセル
    "SUGGEST_SLOT",      # 空き時間候補提案（v2以降）
]

# ===== JSONスキーマ（Pydantic） =====

class Reminder(BaseModel):
    """リマインダー"""
    offset_minutes: int
    channel: Literal["push", "email", "sms"] = "push"

class CreateEventPayload(BaseModel):
    """CREATE_EVENT payload"""
    title: str
    calendar_hint: Optional[str] = None
    start: Optional[str] = None  # ISO 8601 format or null
    end: Optional[str] = None
    all_day: bool = False
    location: Optional[str] = None
    source_url: Optional[str] = None
    recurrence: Optional[str] = None
    reminders: List[Reminder] = []
    notes: Optional[str] = None
    importance: Literal["low", "normal", "high"] = "normal"
    relative_expression: Optional[str] = None
    date_is_ambiguous: bool = False

class UpdateEventPayload(BaseModel):
    """UPDATE_EVENT payload"""
    event_id: str
    patch: Dict

class DeleteEventPayload(BaseModel):
    """DELETE_EVENT payload"""
    event_id: str

class ListAgendaPayload(BaseModel):
    """LIST_AGENDA payload"""
    from_dt: Optional[str] = None  # ISO 8601 format or null
    to_dt: Optional[str] = None
    calendar_filters: Optional[List[str]] = None
    view: Literal["day", "week", "month"] = "day"
    relative_expression: Optional[str] = None

class CreateTaskPayload(BaseModel):
    """CREATE_TASK payload"""
    title: str
    calendar_hint: Optional[str] = None
    due: Optional[str] = None
    notes: Optional[str] = None
    importance: Literal["low", "normal", "high"] = "normal"
    relative_expression: Optional[str] = None
    date_is_ambiguous: bool = False

class UpdateTaskPayload(BaseModel):
    """UPDATE_TASK payload"""
    task_id: str
    patch: Dict

class AICalendarRequest(BaseModel):
    """AIカレンダーリクエスト"""
    intent: str
    request_id: str
    payload: Dict

# ===== システムプロンプト（ユーザー指定仕様） =====

SYSTEM_PROMPT = """あなたはスケジュールAIです。
ユーザーの日本語の指示からカレンダー予定やタスクを自動生成します。

出力は必ず JSON 1つだけにします。
自然文は一切書かず、余計なキーも追加しません。

jsonのトップレベルには次の3つのキーを必ず含めてください:
- "intent": インテント名 (CREATE_EVENT / UPDATE_EVENT / DELETE_EVENT / LIST_AGENDA / CREATE_TASK など)
- "request_id": 適当な一意ID文字列
- "payload": インテントごとの情報オブジェクト

日付・時間はすべて ISO8601 (YYYY-MM-DDThh:mm:ss+09:00) 形式で出力します。
日付が曖昧な場合は、"date_is_ambiguous": true を payload に追加し、そのまま推定した値を "start" に入れてください。

「来週の火曜日」「明日の朝」など相対表現は、現在日時 (CURRENT_DATETIME) を基準に計算してください。
CURRENT_DATETIME は外部から与えられるプレースホルダとして扱い、実際の計算はシステム側で行う場合は、
relative_expression フィールドに原文を保持してください。

【現在日時】
CURRENT_DATETIME: {current_datetime}

【カレンダーヒント推定ルール】
- 病院、眼科、歯科、クリニック、健診、検診、糖尿病 → "健康"
- 保育園、幼稚園、学校、子供、こども → "子供"
- 会議、ミーティング、打ち合わせ、商談、プレゼン → "仕事"
- 年金、役所、市役所、区役所 → "年金"
- ライブ、配信、コンサート、イベント → "ライブ"
- ゴミ出し、掃除、買い物 → "生活"
- その他 → "自分"

【重要度ルール】
- 病院、クリニック、検診、重要、緊急 → "high"
- 会議、ミーティング、打ち合わせ → "normal"
- その他 → "normal"

必ず有効な JSON のみを出力してください。
コメント、説明文、日本語の文章は一切書かないでください。
"""

# ===== Few-shot examples（ユーザー指定仕様） =====

FEW_SHOT_EXAMPLES = [
    {
        "user": "8月8日の15時半から1時間、糖尿病クリニック。30分前に教えて。",
        "assistant": json.dumps({
            "intent": "CREATE_EVENT",
            "request_id": "req-001",
            "payload": {
                "title": "糖尿病クリニック",
                "calendar_hint": "健康",
                "start": "2025-08-08T15:30:00+09:00",
                "end": "2025-08-08T16:30:00+09:00",
                "all_day": False,
                "location": None,
                "source_url": None,
                "recurrence": None,
                "reminders": [
                    {
                        "offset_minutes": 30,
                        "channel": "push"
                    }
                ],
                "notes": None,
                "importance": "high",
                "relative_expression": None,
                "date_is_ambiguous": False
            }
        }, ensure_ascii=False)
    },
    {
        "user": "明日の朝8時にゴミ出しのリマインド。",
        "assistant": json.dumps({
            "intent": "CREATE_TASK",
            "request_id": "req-002",
            "payload": {
                "title": "ゴミ出し",
                "calendar_hint": "生活",
                "due": None,
                "notes": None,
                "importance": "normal",
                "relative_expression": "明日の朝8時",
                "date_is_ambiguous": True
            }
        }, ensure_ascii=False)
    },
    {
        "user": "今日の予定を教えて。",
        "assistant": json.dumps({
            "intent": "LIST_AGENDA",
            "request_id": "req-003",
            "payload": {
                "from_dt": None,
                "to_dt": None,
                "calendar_filters": None,
                "view": "day",
                "relative_expression": "今日"
            }
        }, ensure_ascii=False)
    },
    {
        "user": "来週の火曜日14時に歯医者",
        "assistant": json.dumps({
            "intent": "CREATE_EVENT",
            "request_id": "req-004",
            "payload": {
                "title": "歯医者",
                "calendar_hint": "健康",
                "start": None,
                "end": None,
                "all_day": False,
                "location": None,
                "source_url": None,
                "recurrence": None,
                "reminders": [
                    {
                        "offset_minutes": 30,
                        "channel": "push"
                    }
                ],
                "notes": None,
                "importance": "high",
                "relative_expression": "来週の火曜日14時",
                "date_is_ambiguous": True
            }
        }, ensure_ascii=False)
    },
    {
        "user": "明日の朝9時にミーティング、1時間くらい",
        "assistant": json.dumps({
            "intent": "CREATE_EVENT",
            "request_id": "req-005",
            "payload": {
                "title": "ミーティング",
                "calendar_hint": "仕事",
                "start": None,
                "end": None,
                "all_day": False,
                "location": None,
                "source_url": None,
                "recurrence": None,
                "reminders": [
                    {
                        "offset_minutes": 15,
                        "channel": "push"
                    }
                ],
                "notes": None,
                "importance": "normal",
                "relative_expression": "明日の朝9時",
                "date_is_ambiguous": True
            }
        }, ensure_ascii=False)
    }
]

# ===== 自然文 → JSON 変換関数 =====

def parse_natural_language(user_input: str, context: Optional[Dict] = None) -> Dict:
    """
    自然文からインテントとpayloadを抽出
    
    Args:
        user_input: ユーザーの自然文入力
        context: 会話コンテキスト（直近のイベントID等）
    
    Returns:
        AICalendarRequest の dict
    """
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(current_datetime=current_datetime)}
    ]
    
    # Few-shot examples
    for example in FEW_SHOT_EXAMPLES:
        messages.append({"role": "user", "content": example["user"]})
        messages.append({"role": "assistant", "content": example["assistant"]})
    
    # User input with template
    user_prompt = f"""次のユーザー発話を解析して、予定またはタスクを作成してください。

【ユーザー発話】
{user_input}

必ず有効な JSON のみを出力してください。
コメント、説明文、日本語の文章は一切書かないでください。"""
    
    messages.append({"role": "user", "content": user_prompt})
    
    try:
        openai_client = get_openai_client()
        response = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.1,
            max_tokens=1000
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Extract JSON from code block if present
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(result_text)
        
        # Handle CONTEXT_REQUIRED for event_id
        if result.get("payload", {}).get("event_id") == "CONTEXT_REQUIRED":
            if context and context.get("last_event_id"):
                result["payload"]["event_id"] = context["last_event_id"]
        
        # Resolve relative expressions if present
        if result.get("payload", {}).get("relative_expression"):
            result = resolve_relative_datetime(result)
        
        return result
    
    except Exception as e:
        print(f"Error parsing natural language: {e}")
        return {
            "intent": "UNKNOWN",
            "request_id": f"req_{int(datetime.now().timestamp())}",
            "payload": {},
            "error": str(e)
        }

def resolve_relative_datetime(result: Dict) -> Dict:
    """
    相対日時表現を絶対日時に解決
    
    Args:
        result: parse_natural_language の結果
    
    Returns:
        解決後の result
    """
    relative_expr = result["payload"].get("relative_expression", "")
    now = datetime.now()
    
    # 明日
    if "明日" in relative_expr:
        target_date = now + timedelta(days=1)
        
        # 時刻抽出
        time_match = re.search(r'(\d{1,2})時', relative_expr)
        if time_match:
            hour = int(time_match.group(1))
            target_datetime = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            if result["intent"] == "CREATE_EVENT":
                result["payload"]["start"] = target_datetime.strftime("%Y-%m-%dT%H:%M:%S+09:00")
                # デフォルト1時間
                result["payload"]["end"] = (target_datetime + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S+09:00")
            elif result["intent"] == "CREATE_TASK":
                result["payload"]["due"] = target_datetime.strftime("%Y-%m-%dT%H:%M:%S+09:00")
    
    # 今日
    elif "今日" in relative_expr:
        if result["intent"] == "LIST_AGENDA":
            result["payload"]["from_dt"] = now.replace(hour=0, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S+09:00")
            result["payload"]["to_dt"] = now.replace(hour=23, minute=59, second=59, microsecond=0).strftime("%Y-%m-%dT%H:%M:%S+09:00")
    
    # 来週の火曜日
    elif "来週" in relative_expr:
        days_ahead = 7 - now.weekday() + 1  # 次の火曜日（1=火曜）
        if "火曜" in relative_expr:
            days_ahead = 7 - now.weekday() + 1
        elif "水曜" in relative_expr:
            days_ahead = 7 - now.weekday() + 2
        elif "木曜" in relative_expr:
            days_ahead = 7 - now.weekday() + 3
        elif "金曜" in relative_expr:
            days_ahead = 7 - now.weekday() + 4
        
        target_date = now + timedelta(days=days_ahead)
        
        # 時刻抽出
        time_match = re.search(r'(\d{1,2})時', relative_expr)
        if time_match:
            hour = int(time_match.group(1))
            target_datetime = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            if result["intent"] == "CREATE_EVENT":
                result["payload"]["start"] = target_datetime.strftime("%Y-%m-%dT%H:%M:%S+09:00")
                result["payload"]["end"] = (target_datetime + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S+09:00")
    
    return result

# ===== テスト用 =====

if __name__ == "__main__":
    test_inputs = [
        "8月8日の15時半から1時間、糖尿病クリニック。30分前に教えて。",
        "明日の朝8時にゴミ出しのリマインド。",
        "今日の予定を教えて。",
        "来週の火曜日14時に歯医者",
        "明日の朝9時にミーティング、1時間くらい"
    ]
    
    for test_input in test_inputs:
        print(f"\n入力: {test_input}")
        result = parse_natural_language(test_input)
        print(f"結果: {json.dumps(result, ensure_ascii=False, indent=2)}")
