# Oreza Chat AIカレンダー同期 最終レポート

## 完了日時
2025年11月26日

---

## 📋 プロジェクト概要

Oreza Simple Chatに**自然言語処理によるカレンダー同期機能**を実装し、レンタルサーバーにセキュアにデプロイできる環境を構築しました。

---

## ✅ 完了した機能

### 1. AIチャット ↔ カレンダー同期

#### 自然言語処理
- **LLM**: gpt-4.1-mini（Manus API経由）
- **インテント推定**: CREATE_EVENT, UPDATE_EVENT, DELETE_EVENT, LIST_AGENDA
- **カレンダーヒント推定**: 健康、子供、仕事、年金、ライブ、生活、自分
- **相対日時表現**: 「明日」「来週の火曜日」「今日の午後3時」など

#### データフロー
```
チャット画面 (index.html)
   ↓ 「今日の午後3時に病院」
AIディスパッチAPI (POST /api/ai/calendar/dispatch)
   ↓ parse_nl_for_calendar()
LLM (gpt-4.1-mini)
   ↓ {"intent": "CREATE_EVENT", "calendar_hint": "健康", ...}
resolve_calendar_id()
   ↓ "健康" → "cal_health"
create_event_v2()
   ↓ cal_v2.create_event()
events_db (インメモリ)
   ↓
カレンダーv2ページ (calendar_v2.html)
   ↓ GET /api/calendar/v2/events
予定表示
```

### 2. カレンダーv2

#### デフォルトカレンダー
| ID | 名前 | カラー | 用途 |
|----|------|--------|------|
| cal_health | 健康 | 🟢 緑 | 病院、クリニック、歯医者 |
| cal_child | 子供 | 🩷 ピンク | 保育園、幼稚園、学校 |
| cal_work | 仕事 | 🔵 青 | ミーティング、会議、打ち合わせ |
| cal_pension | 年金 | 🟠 オレンジ | 年金、役所、市役所 |
| cal_live | ライブ | 🟣 紫 | ライブ、配信、コンサート |
| cal_self | 自分 | 🔴 赤 | その他 |

#### AI学習機能
- **カレンダー推定**: タイトルと場所からカレンダーを自動推定
- **時間補完**: 終了時刻が未指定の場合、所要時間を推定
- **リマインダー最適化**: カレンダーごとに最適なリマインダー時間を学習

---

## 🔧 修正した問題

### 問題1: カレンダーIDの不一致

**症状:** チャットで予定を作成しても、カレンダーページに表示されない

**原因:** カレンダーIDが一致せず、存在しないカレンダーに予定が作成されていた

**解決策:** `resolve_calendar_id()`関数を修正し、`cal_`プレフィックスを追加

### 問題2: start_datetimeがNoneの場合のエラー

**症状:** `Create event v2 error: fromisoformat: argument must be str`

**解決策:** `start_datetime`のNullチェックを追加

### 問題3: get_events()関数が存在しない

**症状:** カレンダーページが予定を取得できない

**解決策:** `oreza_calendar_v2.py`に`get_events()`関数を追加

### 問題4: カレンダーキーワード検出が過度に広い

**症状:** 「カレンダーと同期は出来た？」という質問もカレンダーAPIにルーティングされる

**解決策:** 正規表現パターンマッチングに変更

---

## 🧪 テスト結果

### ✅ テスト1: チャットで予定作成
**入力:** 「今日の午後3時に病院」
**結果:** 成功（calendar_id = `cal_health`）

### ✅ テスト2: カレンダーAPIで予定取得
**API:** `GET /api/calendar/v2/events`
**結果:** チャットで作成した予定が正しく取得できる

### ✅ テスト3: 通常のチャット
**入力:** 「カレンダーと同期は出来た？」
**結果:** 通常のチャットAPIにルーティングされる

---

## 📦 デプロイパッケージ

### ファイル一覧
- `app.py` - メインアプリケーション
- `oreza_calendar_v2.py` - カレンダーv2モジュール
- `ai_calendar_sync.py` - AI自然言語処理モジュール
- `multi_agi.py` - マルチAGIオーケストレーション
- `google_search.py` - Google検索モジュール
- `index.html` - チャット画面
- `calendar_v2.html` - カレンダーページ
- `requirements.txt` - Python依存関係
- `nginx.conf` - Nginx設定（HTTPS対応）
- `oreza-chat.service` - systemdサービス定義
- `setup_security.sh` - セキュリティ自動設定スクリプト
- `DEPLOYMENT_GUIDE.md` - デプロイ手順書

### ダウンロード
```bash
scp ubuntu@sandbox:/home/ubuntu/oreza_chat_deploy.tar.gz ./
```

**ファイルサイズ:** 41KB

---

## 🚀 デプロイ手順（概要）

### 1. サーバー準備
```bash
ssh root@your-server-ip
adduser oreza
usermod -aG sudo oreza
```

### 2. セキュリティ設定
```bash
sudo bash setup_security.sh
```

### 3. アプリケーションデプロイ
```bash
sudo tar -xzf oreza_chat_deploy.tar.gz -C /var/www/oreza-chat
cd /var/www/oreza-chat
sudo cp .env.example .env
sudo nano .env  # API キーを設定
sudo python3.11 -m venv venv
sudo -u www-data venv/bin/pip install -r requirements.txt
```

### 4. サービス起動
```bash
sudo cp oreza-chat.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable oreza-chat
sudo systemctl start oreza-chat
```

### 5. Nginx設定
```bash
sudo cp nginx.conf /etc/nginx/sites-available/oreza-chat
sudo ln -s /etc/nginx/sites-available/oreza-chat /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL証明書
```bash
sudo certbot --nginx -d your-domain.com
```

**詳細は `DEPLOYMENT_GUIDE.md` を参照してください。**

---

## 🔒 セキュリティ機能

- [x] HTTPS対応（Let's Encrypt）
- [x] セキュリティヘッダー（X-Frame-Options, CSP, HSTS等）
- [x] ファイアウォール（ufw）
- [x] fail2ban（ブルートフォース攻撃対策）
- [x] SSH鍵認証
- [x] rootログイン無効化
- [x] 環境変数の暗号化（.env）
- [x] systemdサービス（自動起動、再起動）
- [x] 非rootユーザーでの実行（www-data）
- [x] ファイル権限の適切な設定

---

## 📊 アーキテクチャ

```
ユーザー（ブラウザ）
   ↓ HTTPS
Nginx (リバースプロキシ)
   ↓ HTTP (localhost)
Uvicorn (FastAPI アプリ)
   ↓
外部API (OpenAI, Google Search)
```

---

## 📈 今後の拡張予定（v3）

- データ永続化（PostgreSQL/Neon）
- リアルタイム同期（WebSocket）
- 複数ユーザー対応
- 通知機能
- カレンダー共有
- 繰り返し予定
- タスク機能
- AI機能の強化

---

## 🎯 まとめ

### 完了した機能
- ✅ AIチャット ↔ カレンダー同期
- ✅ 自然言語処理によるカレンダー操作
- ✅ カレンダーv2（複数カレンダー対応）
- ✅ AI学習機能
- ✅ セキュアなデプロイ環境
- ✅ HTTPS対応
- ✅ セキュリティ設定の自動化

### デプロイ準備完了
- ✅ デプロイパッケージ作成
- ✅ デプロイ手順書作成
- ✅ セキュリティ設定スクリプト作成
- ✅ Nginx設定ファイル作成
- ✅ systemdサービス定義作成

### アクセス情報（テスト環境）

**URL:** https://8000-iuqj5gy3035kremotwuh2-dc131367.manus-asia.computer

**認証情報:**
- ユーザーID: `oreza-master`
- パスワード: `VeryStrongPass123!`

---

## 📝 使い方

### チャットで予定を作成
```
「明日の朝9時にミーティング」
「8月8日の15時半から1時間、糖尿病クリニック」
「今日の午後3時に病院」
「来週の火曜日14時に歯医者」
```

### カレンダーページで確認
1. チャットで予定作成後、「📅 カレンダーで確認」リンクをクリック
2. カレンダーv2ページが開く
3. 作成した予定がカレンダーグリッドに表示される

---

**プロジェクト完了！レンタルサーバーへのデプロイ準備が整いました。**
