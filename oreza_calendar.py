"""
Oreza AIカレンダー v1
自然文から予定・タスクを作成し、検索結果から予定に変換する機能を提供
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrezaCalendar:
    """Oreza AIカレンダーのコアクラス"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://api.openai.com/v1"
        )
        self.events = []  # v1では in-memory（将来的にDB化）
        self.tasks = []
        
    def parse_natural_language(self, text: str) -> Dict:
        """
        自然文を解析してイベント/タスクのJSONに変換
        
        例: 「来週火曜の15時に歯医者、リマインドは30分前」
        → Event JSON
        """
        prompt = f"""
あなたは予定・タスク抽出の専門家です。以下のテキストから予定またはタスクの情報を抽出してください。

テキスト: {text}

以下のJSON形式で出力してください:

{{
  "type": "event" または "task",
  "title": "予定/タスクのタイトル（動詞+対象）",
  "description": "詳細説明（あれば）",
  "start_datetime": "YYYY-MM-DD HH:MM"（予定の場合）,
  "end_datetime": "YYYY-MM-DD HH:MM"（予定の場合、なければnull）,
  "location": "場所（あれば）",
  "duration_minutes": 30（所要時間の推定、なければ30分）,
  "reminder_minutes": 30（リマインド時間、「30分前」なら30）,
  "due_date": "YYYY-MM-DD"（タスクの場合）,
  "priority": "high" | "medium" | "low"
}}

注意:
- 日時が曖昧な場合は、現在時刻を基準に推定してください
- 今日は {datetime.now().strftime("%Y-%m-%d %H:%M")} です
- 「来週火曜」「明日」「今週末」などを具体的な日時に変換してください
- リマインドが指定されていない場合は、30分前をデフォルトとしてください
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "あなたは予定・タスク抽出の専門家です。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # JSONを抽出（```json ... ``` の場合も対応）
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            parsed = json.loads(result_text)
            logger.info(f"Parsed event/task: {parsed}")
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing natural language: {e}")
            return {
                "type": "task",
                "title": text[:50],
                "description": text,
                "due_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                "priority": "medium"
            }
    
    def parse_search_result(self, title: str, url: str, snippet: str) -> Dict:
        """
        検索結果から予定/タスクのテンプレートを生成
        
        例: 「パスポート更新　千葉」の検索結果
        → タイトル、URL、日程情報を抽出
        """
        prompt = f"""
以下の検索結果から、予定またはタスクの情報を抽出してください。

タイトル: {title}
URL: {url}
スニペット: {snippet}

以下のJSON形式で出力してください:

{{
  "type": "event" または "task",
  "title": "予定/タスクのタイトル（動詞+対象）",
  "description": "詳細説明",
  "location": "場所（あれば）",
  "source_url": "{url}",
  "due_date": "YYYY-MM-DD"（締切がある場合）,
  "priority": "high" | "medium" | "low",
  "estimated_duration_minutes": 60（推定所要時間）
}}

注意:
- スニペットから日程情報があれば抽出してください
- 場所情報があれば抽出してください
- タイトルは「〜する」という形にしてください（例: 「パスポートを更新する」）
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "あなたは検索結果から予定・タスクを抽出する専門家です。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # JSONを抽出
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            parsed = json.loads(result_text)
            parsed["source_url"] = url
            logger.info(f"Parsed search result: {parsed}")
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing search result: {e}")
            return {
                "type": "task",
                "title": title[:50],
                "description": snippet,
                "source_url": url,
                "priority": "medium"
            }
    
    def create_event(self, event_data: Dict) -> Dict:
        """イベントを作成"""
        event = {
            "id": f"evt_{len(self.events) + 1}",
            "type": "event",
            "title": event_data.get("title"),
            "description": event_data.get("description", ""),
            "start_datetime": event_data.get("start_datetime"),
            "end_datetime": event_data.get("end_datetime"),
            "location": event_data.get("location", ""),
            "reminder_minutes": event_data.get("reminder_minutes", 30),
            "source_url": event_data.get("source_url", ""),
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        self.events.append(event)
        logger.info(f"Created event: {event['id']}")
        return event
    
    def create_task(self, task_data: Dict) -> Dict:
        """タスクを作成"""
        task = {
            "id": f"tsk_{len(self.tasks) + 1}",
            "type": "task",
            "title": task_data.get("title"),
            "description": task_data.get("description", ""),
            "due_date": task_data.get("due_date"),
            "priority": task_data.get("priority", "medium"),
            "source_url": task_data.get("source_url", ""),
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        self.tasks.append(task)
        logger.info(f"Created task: {task['id']}")
        return task
    
    def get_today_items(self) -> Dict:
        """今日の予定とタスクを取得"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        today_events = [
            e for e in self.events
            if e.get("start_datetime", "").startswith(today)
        ]
        
        today_tasks = [
            t for t in self.tasks
            if t.get("due_date", "").startswith(today)
        ]
        
        return {
            "date": today,
            "events": sorted(today_events, key=lambda x: x.get("start_datetime", "")),
            "tasks": sorted(today_tasks, key=lambda x: x.get("priority", "medium"), reverse=True)
        }
    
    def get_week_items(self) -> List[Dict]:
        """今週の予定とタスクを取得"""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        week_events = [
            e for e in self.events
            if week_start.strftime("%Y-%m-%d") <= e.get("start_datetime", "")[:10] <= week_end.strftime("%Y-%m-%d")
        ]
        
        week_tasks = [
            t for t in self.tasks
            if week_start.strftime("%Y-%m-%d") <= t.get("due_date", "") <= week_end.strftime("%Y-%m-%d")
        ]
        
        return {
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "events": sorted(week_events, key=lambda x: x.get("start_datetime", "")),
            "tasks": sorted(week_tasks, key=lambda x: x.get("due_date", ""))
        }
    
    def update_status(self, item_id: str, status: str) -> bool:
        """予定/タスクのステータスを更新"""
        for event in self.events:
            if event["id"] == item_id:
                event["status"] = status
                logger.info(f"Updated event {item_id} status to {status}")
                return True
        
        for task in self.tasks:
            if task["id"] == item_id:
                task["status"] = status
                logger.info(f"Updated task {item_id} status to {status}")
                return True
        
        return False
    
    def delete_item(self, item_id: str) -> bool:
        """予定/タスクを削除"""
        self.events = [e for e in self.events if e["id"] != item_id]
        self.tasks = [t for t in self.tasks if t["id"] != item_id]
        logger.info(f"Deleted item {item_id}")
        return True

# グローバルインスタンス
calendar = OrezaCalendar()
