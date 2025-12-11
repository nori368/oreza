"""
Oreza AIカレンダー v2
- 複数カレンダー対応
- AI学習機能（カレンダー振り分け、時間補完、通知最適化）
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pydantic import BaseModel
import os
from openai import OpenAI
import json
import re

# OpenAI APIクライアント
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.openai.com/v1"
)

# ===== データモデル =====

class Calendar(BaseModel):
    """カレンダー"""
    id: str
    name: str
    color: str  # hex color code
    is_visible: bool = True
    created_at: str = datetime.now().isoformat()

class Event(BaseModel):
    """予定"""
    id: str
    calendar_id: str
    title: str
    description: str = ""
    start_datetime: str
    end_datetime: str
    location: str = ""
    url: str = ""
    is_all_day: bool = False
    recurrence: Optional[str] = None  # "daily", "weekly", "monthly", etc.
    reminder_minutes: int = 30
    status: str = "pending"  # pending, completed, cancelled
    created_at: str = datetime.now().isoformat()

class LearningData(BaseModel):
    """AI学習データ"""
    event_patterns: Dict[str, Dict] = {}  # タイトルパターン -> カレンダーID, 所要時間等
    notification_preferences: Dict[str, int] = {}  # カレンダーID -> デフォルトリマインド時間
    calendar_combinations: List[List[str]] = []  # よく使うカレンダー組み合わせ
    time_patterns: Dict[str, int] = {}  # イベントタイプ -> 平均所要時間（分）

# ===== インメモリストレージ =====

calendars_db: Dict[str, Calendar] = {}
events_db: Dict[str, Event] = {}
learning_data = LearningData()

# デフォルトカレンダーの作成
default_calendars = [
    Calendar(id="cal_self", name="自分", color="#E91E63"),
    Calendar(id="cal_child", name="子供", color="#F48FB1"),
    Calendar(id="cal_work", name="仕事", color="#2196F3"),
    Calendar(id="cal_health", name="健康", color="#4CAF50"),
    Calendar(id="cal_pension", name="年金", color="#FF9800"),
    Calendar(id="cal_live", name="ライブ", color="#9C27B0"),
]

for cal in default_calendars:
    calendars_db[cal.id] = cal

# ===== AI学習機能 =====

def predict_calendar(title: str, location: str = "") -> str:
    """
    タイトルと場所からカレンダーを推定
    """
    text = f"{title} {location}".lower()
    
    # キーワードベースの推定
    if any(keyword in text for keyword in ["病院", "眼科", "歯科", "クリニック", "健診", "検診", "糖尿病"]):
        return "cal_health"
    elif any(keyword in text for keyword in ["保育園", "幼稚園", "学校", "子供", "こども"]):
        return "cal_child"
    elif any(keyword in text for keyword in ["会議", "ミーティング", "打ち合わせ", "商談", "プレゼン"]):
        return "cal_work"
    elif any(keyword in text for keyword in ["年金", "役所", "市役所", "区役所"]):
        return "cal_pension"
    elif any(keyword in text for keyword in ["ライブ", "配信", "コンサート", "イベント"]):
        return "cal_live"
    
    # 学習データから推定
    for pattern, data in learning_data.event_patterns.items():
        if pattern in text:
            return data.get("calendar_id", "cal_self")
    
    return "cal_self"  # デフォルト

def predict_duration(title: str, calendar_id: str) -> int:
    """
    タイトルとカレンダーから所要時間（分）を推定
    """
    text = title.lower()
    
    # キーワードベースの推定
    if any(keyword in text for keyword in ["病院", "眼科", "歯科", "クリニック"]):
        return 60
    elif any(keyword in text for keyword in ["筋トレ", "ジム", "トレーニング"]):
        return 45
    elif any(keyword in text for keyword in ["ライブ", "配信"]):
        return 120
    elif any(keyword in text for keyword in ["会議", "ミーティング"]):
        return 60
    
    # 学習データから推定
    if calendar_id in learning_data.time_patterns:
        return learning_data.time_patterns[calendar_id]
    
    return 30  # デフォルト

def predict_reminder(calendar_id: str, title: str) -> int:
    """
    カレンダーとタイトルからリマインド時間（分）を推定
    """
    text = title.lower()
    
    # 重要度の高い予定
    if any(keyword in text for keyword in ["病院", "役所", "支払い", "締切", "期限"]):
        return 60  # 1時間前
    
    # 学習データから推定
    if calendar_id in learning_data.notification_preferences:
        return learning_data.notification_preferences[calendar_id]
    
    return 30  # デフォルト

def learn_from_event(event: Event):
    """
    イベントから学習
    """
    # タイトルパターンを学習
    pattern_key = event.title[:10].lower()  # 最初の10文字
    if pattern_key not in learning_data.event_patterns:
        learning_data.event_patterns[pattern_key] = {}
    
    learning_data.event_patterns[pattern_key]["calendar_id"] = event.calendar_id
    
    # 所要時間を学習
    start = datetime.fromisoformat(event.start_datetime)
    end = datetime.fromisoformat(event.end_datetime)
    duration = int((end - start).total_seconds() / 60)
    
    if event.calendar_id not in learning_data.time_patterns:
        learning_data.time_patterns[event.calendar_id] = duration
    else:
        # 移動平均
        current_avg = learning_data.time_patterns[event.calendar_id]
        learning_data.time_patterns[event.calendar_id] = int((current_avg + duration) / 2)
    
    # 通知設定を学習
    if event.calendar_id not in learning_data.notification_preferences:
        learning_data.notification_preferences[event.calendar_id] = event.reminder_minutes

# ===== 自然文パーサー（AI） =====

def parse_natural_language_v2(text: str) -> Dict:
    """
    自然文から予定情報を抽出（v2: カレンダー推定付き）
    """
    prompt = f"""
以下の文章から予定情報を抽出してJSON形式で返してください。

文章: {text}

抽出する情報:
- title: 予定のタイトル（動詞+対象の形式で）
- start_datetime: 開始日時（YYYY-MM-DD HH:MM形式、曖昧な表現は具体的な日時に変換）
- location: 場所（あれば）
- description: 説明（あれば）
- is_all_day: 終日予定かどうか（true/false）

現在の日時: {datetime.now().strftime("%Y-%m-%d %H:%M")}

JSON形式で返してください。
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは予定情報を抽出する専門家です。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # JSONを抽出
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            
            # カレンダーを推定
            calendar_id = predict_calendar(
                result.get("title", ""),
                result.get("location", "")
            )
            result["calendar_id"] = calendar_id
            
            # 終了時刻を推定（指定されていない場合）
            if "end_datetime" not in result or not result["end_datetime"]:
                duration = predict_duration(result.get("title", ""), calendar_id)
                start_dt = datetime.fromisoformat(result["start_datetime"])
                end_dt = start_dt + timedelta(minutes=duration)
                result["end_datetime"] = end_dt.strftime("%Y-%m-%d %H:%M")
            
            # リマインド時間を推定
            reminder = predict_reminder(calendar_id, result.get("title", ""))
            result["reminder_minutes"] = reminder
            
            return result
        else:
            return {"error": "JSON形式の抽出に失敗しました"}
    
    except Exception as e:
        return {"error": str(e)}

# ===== CRUD操作 =====

def create_calendar(name: str, color: str) -> Calendar:
    """カレンダーを作成"""
    cal_id = f"cal_{len(calendars_db) + 1}"
    calendar = Calendar(id=cal_id, name=name, color=color)
    calendars_db[cal_id] = calendar
    return calendar

def get_calendars() -> List[Calendar]:
    """すべてのカレンダーを取得"""
    return list(calendars_db.values())

def update_calendar_visibility(calendar_id: str, is_visible: bool):
    """カレンダーの表示/非表示を切り替え"""
    if calendar_id in calendars_db:
        calendars_db[calendar_id].is_visible = is_visible

def create_event(event_data: Dict) -> Event:
    """予定を作成"""
    event_id = f"evt_{len(events_db) + 1}"
    event = Event(id=event_id, **event_data)
    events_db[event_id] = event
    
    # 学習
    learn_from_event(event)
    
    return event

def get_events(start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Event]:
    """予定を取得（日付範囲指定可能）"""
    if start_date and end_date:
        result = []
        for event in events_db.values():
            event_date = event.start_datetime[:10]
            if start_date <= event_date <= end_date:
                result.append(event)
        return sorted(result, key=lambda x: x.start_datetime)
    else:
        # 全予定を返す
        return sorted(list(events_db.values()), key=lambda x: x.start_datetime)

def get_events_by_date_range(start_date: str, end_date: str) -> List[Event]:
    """日付範囲で予定を取得"""
    return get_events(start_date, end_date)

def get_events_by_calendar(calendar_id: str) -> List[Event]:
    """カレンダーIDで予定を取得"""
    return [e for e in events_db.values() if e.calendar_id == calendar_id]

def update_event_status(event_id: str, status: str):
    """予定のステータスを更新"""
    if event_id in events_db:
        events_db[event_id].status = status

def delete_event(event_id: str):
    """予定を削除"""
    if event_id in events_db:
        del events_db[event_id]

# ===== ビュー提案 =====

def suggest_calendar_views() -> List[Dict]:
    """よく使うカレンダー組み合わせを提案"""
    views = [
        {
            "name": "健康モード",
            "calendar_ids": ["cal_health", "cal_child"],
            "description": "健康と子供の医療関連"
        },
        {
            "name": "仕事モード",
            "calendar_ids": ["cal_work", "cal_self"],
            "description": "仕事と個人の予定"
        },
        {
            "name": "家族モード",
            "calendar_ids": ["cal_self", "cal_child"],
            "description": "家族イベントと学校関係"
        },
    ]
    return views



# ===== 予定通知機能 =====

def get_upcoming_notifications() -> List[Dict]:
    """
    ログイン時に表示する予定通知を取得
    - 当日の予定
    - 翌日の予定
    """
    from datetime import datetime, timedelta
    
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    
    notifications = []
    
    # 当日の予定
    today_events = get_events(today, today)
    for event in today_events:
        if event.status != "cancelled":
            notifications.append({
                "type": "today",
                "event_id": event.id,
                "title": event.title,
                "start_datetime": event.start_datetime,
                "calendar_name": calendars_db.get(event.calendar_id, {}).name if event.calendar_id in calendars_db else "不明",
                "message": f"【本日】{event.title} - {event.start_datetime[11:16]}"
            })
    
    # 翌日の予定
    tomorrow_events = get_events(tomorrow, tomorrow)
    for event in tomorrow_events:
        if event.status != "cancelled":
            notifications.append({
                "type": "tomorrow",
                "event_id": event.id,
                "title": event.title,
                "start_datetime": event.start_datetime,
                "calendar_name": calendars_db.get(event.calendar_id, {}).name if event.calendar_id in calendars_db else "不明",
                "message": f"【明日】{event.title} - {event.start_datetime[11:16]}"
            })
    
    return notifications

def get_today_date() -> str:
    """現在の日付を取得（YYYY-MM-DD形式）"""
    return datetime.now().strftime("%Y-%m-%d")
