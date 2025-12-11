# 🚀 PythonAnywhere デプロイガイド

Oreza Chat & Shopping PlatformをPythonAnywhereにデプロイする詳細な手順

---

## 📋 前提条件

- PythonAnywhereアカウント（無料または有料）
- OpenAI APIキー
- Google Custom Search APIキーとCSE ID

---

## ステップ1: アカウント作成

1. [PythonAnywhere](https://www.pythonanywhere.com)にアクセス
2. 「Start running Python online in less than a minute!」の下の「Create a Beginner account」をクリック
3. ユーザー名、メールアドレス、パスワードを入力して登録
4. メール認証を完了

**注意:** 無料プランは以下の制限があります:
- CPU時間: 1日100秒
- 外部API: ホワイトリストのみ（OpenAI APIは許可済み）
- ディスク容量: 512MB
- カスタムドメイン: 不可（`<username>.pythonanywhere.com`のみ）

---

## ステップ2: ファイルのアップロード

### 方法A: Webインターフェースから（推奨）

1. PythonAnywhereダッシュボードにログイン
2. 「Files」タブをクリック
3. 「Upload a file」ボタンをクリック
4. 以下のファイルを順番にアップロード:

**必須ファイル:**
```
app.py
multi_agi.py
shopping.py
google_search.py
quantum_memory.py
failure_learning.py
requirements.txt
wsgi.py
.env
index.html
shopping.html
```

**ディレクトリ構造:**
```
/home/<username>/oreza_chat/
├── app.py
├── multi_agi.py
├── shopping.py
├── google_search.py
├── quantum_memory.py
├── failure_learning.py
├── requirements.txt
├── wsgi.py
├── .env
├── index.html
├── shopping.html
├── images/
│   └── shopping_icon.png
├── js/
└── css/
```

5. 「New directory」ボタンで `images`, `js`, `css` ディレクトリを作成
6. 画像ファイルを `images/` にアップロード

### 方法B: Bashコンソールから

1. 「Consoles」タブをクリック
2. 「Bash」をクリックして新しいコンソールを開く
3. 以下のコマンドを実行:

```bash
# プロジェクトディレクトリを作成
mkdir -p ~/oreza_chat
cd ~/oreza_chat

# 必要なディレクトリを作成
mkdir -p images js css

# ファイルをアップロード（方法Aで行う）
```

---

## ステップ3: 仮想環境の作成とパッケージのインストール

1. 「Consoles」タブから「Bash」コンソールを開く
2. 以下のコマンドを実行:

```bash
# 仮想環境を作成
mkvirtualenv --python=/usr/bin/python3.11 oreza

# 仮想環境が自動的にアクティブになります
# プロンプトが (oreza) で始まることを確認

# プロジェクトディレクトリに移動
cd ~/oreza_chat

# 依存関係をインストール
pip install -r requirements.txt

# インストールの確認
pip list
```

**注意:** インストールには数分かかる場合があります。

---

## ステップ4: 環境変数の設定

### 方法A: .envファイルを編集

1. 「Files」タブから `/home/<username>/oreza_chat/.env` を開く
2. 以下の内容を入力:

```env
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY_HERE
GOOGLE_CSE_ID=YOUR_GOOGLE_CSE_ID_HERE
MASTER_ID=oreza-master
MASTER_PASSWORD=VeryStrongPass123!
HOST=0.0.0.0
PORT=8000
```

3. 「Save」をクリック

### 方法B: Bashコンソールから

```bash
cd ~/oreza_chat
nano .env
# 上記の内容を貼り付け
# Ctrl+O で保存、Ctrl+X で終了
```

---

## ステップ5: Webアプリの設定

1. 「Web」タブをクリック
2. 「Add a new web app」ボタンをクリック
3. ドメイン名を確認（`<username>.pythonanywhere.com`）
4. 「Next」をクリック
5. 「Manual configuration」を選択
6. 「Python 3.11」を選択
7. 「Next」をクリック

---

## ステップ6: WSGI設定ファイルの編集

1. 「Web」タブの「Code」セクションで、「WSGI configuration file」のリンクをクリック
2. ファイルの内容を**すべて削除**
3. 以下の内容を貼り付け:

```python
import sys
import os
from pathlib import Path

# プロジェクトディレクトリをパスに追加
# ★ <username> を自分のPythonAnywhereユーザー名に置き換える
project_home = '/home/<username>/oreza_chat'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 環境変数を読み込み
from dotenv import load_dotenv
env_path = Path(project_home) / '.env'
load_dotenv(dotenv_path=env_path)

# FastAPIアプリをインポート
from app import app as application

# ASGI-to-WSGI adapter
from asgiref.wsgi import WsgiToAsgi
application = WsgiToAsgi(application)
```

4. `<username>` を自分のPythonAnywhereユーザー名に置き換える
5. 「Save」をクリック

---

## ステップ7: 仮想環境のパスを設定

1. 「Web」タブに戻る
2. 「Virtualenv」セクションで、「Enter path to a virtualenv」に以下を入力:

```
/home/<username>/.virtualenvs/oreza
```

3. `<username>` を自分のユーザー名に置き換える
4. チェックマークをクリック

---

## ステップ8: 静的ファイルの設定

1. 「Web」タブの「Static files」セクションで、「Enter URL」と「Enter path」を入力:

**設定1: 画像**
- URL: `/images/`
- Directory: `/home/<username>/oreza_chat/images/`

**設定2: JavaScript**
- URL: `/js/`
- Directory: `/home/<username>/oreza_chat/js/`

**設定3: CSS**
- URL: `/css/`
- Directory: `/home/<username>/oreza_chat/css/`

2. 各設定で「✓」をクリック

---

## ステップ9: Webアプリをリロード

1. 「Web」タブの上部にある緑色の「Reload <username>.pythonanywhere.com」ボタンをクリック
2. 数秒待つ

---

## ステップ10: 動作確認

1. ブラウザで `https://<username>.pythonanywhere.com` にアクセス
2. ログインページが表示されることを確認
3. ユーザーID: `oreza-master`, パスワード: `VeryStrongPass123!` でログイン
4. チャット機能をテスト
5. 「🛍️ ショッピング」ボタンをクリックしてショッピングページをテスト

---

## 🔧 トラブルシューティング

### エラー: "ImportError: No module named 'app'"

**原因:** WSGIファイルのパスが間違っている

**解決策:**
1. WSGI設定ファイルの `project_home` を確認
2. Bashコンソールで `ls ~/oreza_chat/app.py` を実行してファイルが存在するか確認

### エラー: "ModuleNotFoundError: No module named 'fastapi'"

**原因:** 仮想環境にパッケージがインストールされていない

**解決策:**
```bash
workon oreza
cd ~/oreza_chat
pip install -r requirements.txt
```

### エラー: "500 Internal Server Error"

**原因:** 環境変数が設定されていない、またはコードにエラーがある

**解決策:**
1. 「Web」タブの「Log files」セクションで「Error log」を確認
2. `.env`ファイルが正しく設定されているか確認
3. Bashコンソールで以下を実行してテスト:
   ```bash
   workon oreza
   cd ~/oreza_chat
   python -c "from app import app; print('OK')"
   ```

### エラー: "OpenAI API key is invalid"

**原因:** APIキーが間違っている、または期限切れ

**解決策:**
1. `.env`ファイルの `OPENAI_API_KEY` を確認
2. OpenAIダッシュボードで新しいキーを生成
3. Webアプリをリロード

### ページが表示されない

**原因:** 静的ファイルのパスが間違っている

**解決策:**
1. 「Web」タブの「Static files」セクションを確認
2. Bashコンソールで以下を実行:
   ```bash
   ls ~/oreza_chat/index.html
   ls ~/oreza_chat/shopping.html
   ```

---

## 🔄 アップデート手順

アプリケーションを更新する場合:

1. 「Files」タブから更新したいファイルを開く
2. 編集して「Save」
3. 「Web」タブで「Reload」ボタンをクリック

または、Bashコンソールから:

```bash
cd ~/oreza_chat
# ファイルを編集（nanoまたはvim）
nano app.py
# 保存後、Webアプリをリロード
```

---

## 📊 無料プランの制限と対策

### CPU時間制限（1日100秒）

**対策:**
- 有料プラン（$5/月）にアップグレード
- または、VPSに移行

### 外部API制限

**対策:**
- OpenAI APIはホワイトリストに含まれているため問題なし
- Google APIもホワイトリストに含まれている可能性が高い
- 問題がある場合は有料プランにアップグレード

### ディスク容量（512MB）

**対策:**
- 不要なファイルを削除
- ログファイルを定期的にクリア
- 有料プランにアップグレード

---

## 🎯 本番環境への移行

無料プランで動作確認後、以下のオプションを検討:

### オプション1: PythonAnywhere有料プラン

**Hacker Plan ($5/月):**
- CPU時間無制限
- ディスク容量: 1GB
- カスタムドメイン対応

**Web Developer Plan ($12/月):**
- CPU時間無制限
- ディスク容量: 3GB
- 複数のWebアプリ

### オプション2: VPS + Docker

より高度な制御が必要な場合は、VPSへの移行を検討してください。

詳細は `DEPLOYMENT_GUIDE_DOCKER.md` を参照。

---

## ✅ チェックリスト

デプロイ前に以下を確認:

- [ ] PythonAnywhereアカウントを作成
- [ ] すべてのファイルをアップロード
- [ ] 仮想環境を作成してパッケージをインストール
- [ ] `.env`ファイルにAPIキーを設定
- [ ] Webアプリを作成
- [ ] WSGI設定ファイルを編集
- [ ] 仮想環境のパスを設定
- [ ] 静的ファイルのパスを設定
- [ ] Webアプリをリロード
- [ ] ブラウザでアクセスして動作確認

---

## 📞 サポート

問題が解決しない場合:

1. PythonAnywhereの[フォーラム](https://www.pythonanywhere.com/forums/)で質問
2. [ヘルプページ](https://help.pythonanywhere.com/)を確認
3. エラーログを確認して原因を特定

---

**デプロイ成功をお祈りします！** 🎉
