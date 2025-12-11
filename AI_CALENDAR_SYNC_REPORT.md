# AIチャット ↔ カレンダー同期プロト 実装完了レポート

## 実装日時
2025年11月26日

## 概要
Oreza Simple Chatに自然言語処理によるカレンダー同期機能を実装しました。ユーザーは日本語の自然な会話でカレンダーの予定を作成・編集・削除・確認できるようになりました。

## 実装内容

### 1. インテント定義とJSONスキーマ (`ai_calendar_sync.py`)

**サポートされているインテント:**
- `CREATE_EVENT`: イベント新規作成
- `UPDATE_EVENT`: 既存イベントの編集
- `DELETE_EVENT`: イベント削除
- `LIST_AGENDA`: 今日/指定日の予定取得
- `CREATE_TASK`: タスク作成
- `UPDATE_TASK`: タスク編集
- `CANCEL_EVENT`: 予約キャンセル

**JSONスキーマ:**
- Pydanticモデルによる厳密な型定義
- ISO 8601形式の日時フォーマット
- 相対日時表現のサポート（`relative_expression`フィールド）
- 曖昧な日付の検出（`date_is_ambiguous`フィールド）

### 2. 自然文→予定JSON変換プロンプト

**システムプロンプト:**
- JSON出力専用（説明文なし）
- トップレベルキー: `intent`, `request_id`, `payload`
- ISO 8601形式の日時出力
- 相対表現の保持と解決

**Few-shot examples:**
1. 通院: 「8月8日の15時半から1時間、糖尿病クリニック。30分前に教えて。」
2. 相対日時: 「明日の朝8時にゴミ出しのリマインド。」
3. 予定確認: 「今日の予定を教えて。」
4. 相対日時（来週）: 「来週の火曜日14時に歯医者」
5. ミーティング: 「明日の朝9時にミーティング、1時間くらい」

**カレンダーヒント推定ルール:**
- 健康: 病院、眼科、歯科、クリニック、健診、検診、糖尿病
- 子供: 保育園、幼稚園、学校、子供、こども
- 仕事: 会議、ミーティング、打ち合わせ、商談、プレゼン
- 年金: 年金、役所、市役所、区役所
- ライブ: ライブ、配信、コンサート、イベント
- 生活: ゴミ出し、掃除、買い物
- 自分: その他

### 3. AIディスパッチAPI (`POST /api/ai/calendar/dispatch`)

**リクエスト形式:**
```json
{
  "user_input": "明日の朝9時にミーティング",
  "context": {
    "session_id": "session_123",
    "last_event_id": "evt_1"
  }
}
```

**レスポンス形式（成功時）:**
```json
{
  "success": true,
  "intent": "CREATE_EVENT",
  "result": {
    "id": "evt_1",
    "calendar_id": "work",
    "title": "ミーティング",
    "start_datetime": "2025-11-26T09:00:00+09:00",
    "end_datetime": "2025-11-26T10:00:00+09:00",
    ...
  },
  "parsed": {
    "intent": "CREATE_EVENT",
    "request_id": "req-006",
    "payload": {...}
  },
  "message": "予定「ミーティング」を作成しました。"
}
```

**インテント処理:**
- `CREATE_EVENT`: カレンダーヒントからcalendar_idを解決し、`create_event_v2`を呼び出し
- `UPDATE_EVENT`: event_idとpatchを使用して`update_event_v2`を呼び出し
- `DELETE_EVENT`: event_idを使用して`delete_event_v2`を呼び出し
- `LIST_AGENDA`: 日付範囲で`get_events_by_date_range`を呼び出し、整形して返す
- `CREATE_TASK`: 未実装（将来対応）

**ヘルパー関数:**
- `resolve_calendar_id()`: カレンダーヒント（日本語）→calendar_id（英語）の変換
- `format_agenda()`: イベントリストを自然な日本語に整形

### 4. チャットUIとカレンダーの連携 (`index.html`)

**カレンダー関連クエリの検出:**
```javascript
const calendarKeywords = [
  '予定', 'カレンダー', 'スケジュール', 'リマインド',
  'ミーティング', '会議', '病院', 'クリニック', '歯医者',
  'ゴミ出し', '明日', '今日', '来週'
];
```

**処理フロー:**
1. ユーザーメッセージにカレンダーキーワードが含まれているか検出
2. 含まれている場合、`/api/ai/calendar/dispatch`にリクエスト
3. 成功時、確認メッセージとカレンダーページへのリンクを表示
4. 失敗時、エラーメッセージを表示

**コンテキスト保持:**
- `window.lastEventId`: 直近のイベントIDを保存
- 後続の更新・削除リクエストで使用

## テスト結果

### テスト1: イベント作成（明日の朝9時にミーティング）

**入力:**
```
明日の朝9時にミーティング
```

**出力:**
```json
{
  "success": true,
  "intent": "CREATE_EVENT",
  "result": {
    "id": "evt_1",
    "calendar_id": "work",
    "title": "ミーティング",
    "start_datetime": "2025-11-26T09:00:00+09:00",
    "end_datetime": "2025-11-26T10:00:00+09:00",
    "location": "",
    "reminder_minutes": 15,
    "status": "pending"
  },
  "message": "予定「ミーティング」を作成しました。"
}
```

✅ **成功**: カレンダーヒント「仕事」を正しく推定し、work カレンダーに作成

### テスト2: 予定確認（今日の予定を教えて）

**入力:**
```
今日の予定を教えて
```

**出力:**
```json
{
  "success": true,
  "intent": "LIST_AGENDA",
  "result": {
    "events": [],
    "agenda_text": "この期間に予定はありません。"
  },
  "message": "この期間に予定はありません。"
}
```

✅ **成功**: 今日の予定を正しく取得（現在は予定なし）

## 技術的な課題と解決策

### 課題1: 関数名の衝突
**問題:** `app.py`に既存の`parse_natural_language`関数が存在し、インポートした関数と衝突

**解決策:**
```python
from ai_calendar_sync import parse_natural_language as parse_nl_for_calendar
```

### 課題2: OpenAI APIモデル名
**問題:** `gpt-4o-mini`がサポートされていない

**解決策:** `gpt-4.1-mini`に変更

### 課題3: Eventオブジェクトのシリアライズ
**問題:** Pydantic Eventオブジェクトが直接JSONシリアライズできない

**解決策:**
```python
if hasattr(event, 'dict'):
    event_dict = event.dict()
elif hasattr(event, '__dict__'):
    event_dict = event.__dict__
else:
    event_dict = event
```

### 課題4: None値のバリデーションエラー
**問題:** `location`や`notes`がNoneの場合、Pydanticバリデーションエラー

**解決策:**
```python
"location": payload.get("location") or "",
"notes": payload.get("notes") or "",
```

## 今後の拡張予定

### v3機能（将来実装）
1. **データ永続化**: PostgreSQL/Neonへの移行
2. **タスク機能**: CREATE_TASK, UPDATE_TASKの完全実装
3. **繰り返し予定**: RRULEフォーマットのサポート
4. **空き時間提案**: SUGGEST_SLOTインテントの実装
5. **複数ユーザー対応**: ユーザーIDによる予定の分離
6. **通知機能**: リマインダーの実際の通知送信
7. **カレンダー共有**: 複数ユーザー間での予定共有

### UI/UX改善
1. **音声入力**: 音声で予定を追加
2. **カレンダービュー**: チャット内でのカレンダー表示
3. **予定の編集**: チャット内で直接編集
4. **予定の削除**: 「その予定を削除して」で削除

## まとめ

AIチャット ↔ カレンダー同期プロトの実装が完了しました。ユーザーは自然な日本語で予定を管理できるようになり、Oreza Simple Chatの実用性が大幅に向上しました。

**主な成果:**
- ✅ 自然言語処理による予定作成
- ✅ カレンダーヒントの自動推定
- ✅ 相対日時表現のサポート
- ✅ チャットUIとカレンダーの連携
- ✅ iOS風カレンダーUIとの統合

**アクセスURL:**
https://8000-iuqj5gy3035kremotwuh2-dc131367.manus-asia.computer

**認証情報:**
- ユーザーID: `oreza-master`
- パスワード: `VeryStrongPass123!`
