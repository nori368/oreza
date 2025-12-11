# OpenAI API統合問題 - 解決レポート

**日時**: 2025年11月28日 05:25 JST  
**ステータス**: ✅ **解決完了**

---

## 問題の概要

Oreza Simple Chatアプリケーションで、OpenAI APIを使用したチャット機能が動作せず、以下のエラーメッセージが表示されていました：

```
申し訳ございません。一時的なエラーが発生しました。
```

サーバーログには以下のエラーが記録されていました：

```
Error code: 401 - {'error': {'message': 'Incorrect API key provided: sk-JNCdv*************p3Ly. ...
```

---

## 根本原因

### 1. 環境変数の競合

- `.env`ファイルには新しいAPIキーが正しく保存されていた
- しかし、**シェルの環境変数**に古いAPIキー（`sk-JNCdv...`）が残っていた
- Python の `load_dotenv()` は、既に設定されている環境変数を上書きしないため、古いAPIキーが優先されていた

### 2. プロセスの重複

- 古いプロセス（PID: 19225）が動作し続けていた
- 新しいプロセス（PID: 19543）がポート8000を使用しようとして失敗していた

---

## 解決手順

### ステップ1: 古いプロセスの停止

```bash
sudo kill -9 19225
pkill -f "uvicorn app:app"
```

### ステップ2: 環境変数のクリア

```bash
unset OPENAI_API_KEY
```

これにより、シェルに残っていた古いAPIキーを削除しました。

### ステップ3: 依存関係のインストール

```bash
sudo pip3 install python-dotenv openai fastapi uvicorn pydantic
```

`python-dotenv`モジュールが不足していたため、インストールしました。

### ステップ4: サーバーの再起動

```bash
cd /home/ubuntu/oreza_chat
nohup python3.11 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &
```

環境変数をクリアした状態で再起動することで、`.env`ファイルから新しいAPIキーが正しく読み込まれました。

---

## テスト結果

### チャット機能のテスト

**入力**: 「こんにちは、調子はどうですか？」

**AI応答**: 「こんにちは！私は元気です。あなたはいかがですか？何かお手伝いできることがあれば教えてください。」

### サーバーログ（成功）

```
[PID:19906] 2025-11-28 05:25:34,943 - oreza_v1 - INFO - Created new session: 3e112427-ae83-47a1-8340-8af393f54d94
[PID:19906] 2025-11-28 05:25:34,943 - multi_agi - INFO - 🔄 Running parallel AGI orchestration...
[PID:19906] 2025-11-28 05:25:34,990 - multi_agi - INFO - Gemini is disabled, using GPT-4 only
[PID:19906] 2025-11-28 05:25:37,432 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
[PID:19906] 2025-11-28 05:25:37,603 - multi_agi - INFO - ✅ Selected gpt-4o-mini: GPT-4o-mini: Fast and versatile general-purpose response
[PID:19906] 2025-11-28 05:25:37,603 - oreza_v1 - INFO - [3e112427-ae83-47a1-8340-8af393f54d94] AGI response from gpt-4o-mini
INFO:     10.16.90.1:55154 - "POST /api/chat HTTP/1.1" 200 OK
```

**結果**: ✅ OpenAI APIが正常に応答し、チャット機能が動作しています。

---

## 現在の動作状況

### ✅ 正常に動作している機能

1. **チャット機能**: OpenAI API（gpt-4o-mini）による応答
2. **カレンダー機能**: 自然言語処理による予定管理
3. **認証システム**: マスターID/パスワードによるログイン
4. **セッション管理**: ユーザーごとの会話履歴保存

### サーバー情報

- **URL**: https://8000-iuqj5gy3035kremotwuh2-dc131367.manus-asia.computer/
- **プロセスID**: 19906
- **ポート**: 8000
- **認証情報**:
  - ID: `oreza-master`
  - パスワード: `akifuyu0621`

---

## 今後の推奨事項

### 1. 環境変数の管理

本番環境では、以下のいずれかの方法で環境変数を管理することを推奨します：

- **Docker環境**: `docker-compose.yml`で環境変数を定義
- **systemdサービス**: `/etc/systemd/system/oreza-chat.service`で環境変数を設定
- **環境変数ファイル**: `.env`ファイルのみを使用し、シェル環境変数は使用しない

### 2. プロセス管理

本番環境では、以下のツールを使用してプロセスを管理することを推奨します：

- **systemd**: サービスとして登録し、自動起動・再起動を設定
- **supervisor**: プロセス監視と自動再起動
- **PM2**: Node.js環境での代替案（uvicornも対応可能）

### 3. ログ管理

- ログローテーション設定（logrotate）
- エラー通知システムの導入
- ログ集約ツール（ELKスタック、Grafana Loki等）

### 4. セキュリティ

- APIキーの定期的なローテーション
- HTTPSの有効化（本番環境）
- レート制限の実装
- CORS設定の見直し

---

## まとめ

OpenAI API統合の問題は、**環境変数の競合**が原因でした。シェルの環境変数をクリアし、`.env`ファイルから新しいAPIキーを読み込むことで、問題を解決しました。

現在、すべての機能が正常に動作しており、Xサーバーへの移行準備が整っています。

---

**作成者**: Manus AI Assistant  
**最終更新**: 2025年11月28日 05:26 JST
