# 🤖 Oreza Chat & Shopping Platform

AIチャットとショッピング検索を統合したWebプラットフォーム

## ✨ 機能

### 1. AIチャット
- OpenAI GPT-4を使用した高度な会話AI
- Multi-AGI Orchestrator（複数AIモデルの統合）
- Quantum Memory（会話文脈の記憶管理）
- Failure Learning（失敗から学習するシステム）

### 2. ショッピング検索
- Google検索風のクリーンなUI
- Google Custom Search APIによる商品検索
- AIソムリエによる商品分析
- ファッションフィット分析
- 検索履歴とお気に入り機能

## 🚀 デプロイ方法

### オプション1: PythonAnywhere（推奨）

1. [PythonAnywhere](https://www.pythonanywhere.com)でアカウントを作成
2. Filesタブからファイルをアップロード
3. Bashコンソールで仮想環境を作成:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.11 oreza
   pip install -r requirements.txt
   ```
4. Webタブから「Add a new web app」を選択
5. Manual configurationを選択してPython 3.11を選択
6. WSGI設定ファイルを編集（`wsgi.py`の内容をコピー）
7. 環境変数を設定（`.env`ファイルまたはPythonAnywhereの設定）
8. Reloadして起動

詳細は `DEPLOYMENT_GUIDE_PYTHONANYWHERE.md` を参照

### オプション2: Docker + VPS

1. VPS（Vultr, DigitalOcean等）を契約
2. Dockerをインストール
3. リポジトリをクローンまたはファイルをアップロード
4. `.env`ファイルを作成してAPIキーを設定
5. Docker Composeで起動:
   ```bash
   docker-compose up -d
   ```

詳細は `DEPLOYMENT_GUIDE_DOCKER.md` を参照

## 🔧 ローカル開発

### 必要要件
- Python 3.11以上
- pip

### セットアップ

1. リポジトリをクローン（またはファイルをダウンロード）

2. 仮想環境を作成:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. 依存関係をインストール:
   ```bash
   pip install -r requirements.txt
   ```

4. `.env`ファイルを作成:
   ```bash
   cp .env.example .env
   # .envファイルを編集してAPIキーを設定
   ```

5. サーバーを起動:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

6. ブラウザで `http://localhost:8000` にアクセス

## 📁 ファイル構成

```
oreza_chat/
├── app.py                 # FastAPIメインアプリケーション
├── multi_agi.py           # Multi-AGI Orchestrator
├── shopping.py            # ショッピング機能モジュール
├── google_search.py       # Google検索API統合
├── quantum_memory.py      # 会話記憶管理
├── failure_learning.py    # 失敗学習システム
├── index.html             # メインチャットUI
├── shopping.html          # ショッピング検索UI
├── requirements.txt       # Python依存関係
├── .env                   # 環境変数（作成が必要）
├── .env.example           # 環境変数テンプレート
├── wsgi.py                # PythonAnywhere用WSGI設定
├── Dockerfile             # Docker設定
├── docker-compose.yml     # Docker Compose設定
└── README.md              # このファイル
```

## 🔑 環境変数

以下の環境変数を`.env`ファイルに設定してください:

```env
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
GOOGLE_API_KEY=YOUR_KEY_HERE
GOOGLE_CSE_ID=YOUR_CSE_ID_HERE
MASTER_ID=your_username
MASTER_PASSWORD=your_password
```

## 📝 APIエンドポイント

### チャット
- `POST /api/chat` - AIチャット
- `POST /api/login` - ログイン
- `POST /api/logout` - ログアウト
- `GET /api/health` - ヘルスチェック

### ショッピング
- `POST /api/shopping/search` - 商品検索
- `POST /api/shopping/analyze` - AI商品分析
- `POST /api/shopping/fashion-fit` - ファッションフィット分析
- `GET /api/search/history` - 検索履歴取得
- `POST /api/search/favorites` - お気に入り追加
- `GET /api/search/favorites` - お気に入り一覧

## 🎨 技術スタック

**バックエンド:**
- FastAPI
- Python 3.11
- OpenAI API
- Google Custom Search API

**フロントエンド:**
- HTML5/CSS3
- Vanilla JavaScript
- レスポンシブデザイン

## 📄 ライセンス

このプロジェクトは個人利用のために作成されています。

## 🤝 サポート

問題が発生した場合は、以下のドキュメントを参照してください:
- `DEPLOYMENT_OPTIONS.md` - デプロイオプションの比較
- `DEPLOYMENT_GUIDE_PYTHONANYWHERE.md` - PythonAnywhereデプロイガイド
- `DEPLOYMENT_GUIDE_DOCKER.md` - Dockerデプロイガイド

## 🎯 今後の予定

- [ ] 画像検索機能
- [ ] ニュース検索機能
- [ ] 動画検索機能
- [ ] ユーザー登録・ログイン機能
- [ ] パーソナライズされた推薦機能
- [ ] 音声入力機能
- [ ] 画像生成機能
