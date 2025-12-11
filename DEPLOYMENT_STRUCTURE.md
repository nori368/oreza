# Oreza Simple Chat - デプロイ構造

## 公開ディレクトリ構成

### さくらインターネットサーバー

```
/home/orezaai/www/          # 公開ディレクトリ（SERVER_DIR）
├── index.html              # メインHTML
├── app.py                  # FastAPIサーバー
├── multi_agi.py            # Multi-AGIロジック
├── google_search.py        # Google検索機能
├── failure_learning.py     # 失敗学習機能
├── quantum_memory.py       # メモリ管理
├── js/
│   └── main.js            # フロントエンドJS
└── css/                    # CSS（存在する場合）
```

### 公開が必要なファイル

| ファイル | 用途 | 権限 |
|---------|------|------|
| `index.html` | メインHTML | 644 |
| `app.py` | FastAPIサーバー | 644 |
| `multi_agi.py` | Multi-AGI | 644 |
| `google_search.py` | Google検索 | 644 |
| `failure_learning.py` | 失敗学習 | 644 |
| `quantum_memory.py` | メモリ管理 | 644 |
| `js/main.js` | フロントエンドJS | 644 |

### 公開が不要なファイル（.gitignoreに追加済み）

- `__pycache__/` - Pythonキャッシュ
- `*_old.html`, `*_new.html` - 旧バージョン
- `*_stable.py` - バックアップ
- `test.html` - テストファイル
- `*.md` - ドキュメント（README.md以外）
- `IMG_*.jpeg` - スクリーンショット
- `*.sh` - サーバー管理スクリプト
- `.env` - 環境変数

---

## ディレクトリ分離（セキュリティ強化後）

### 推奨構成

```
/home/orezaai/
├── www/                    # 公開エリア（Webルート）
│   ├── index.html
│   ├── js/
│   └── css/
├── secure/                 # 非公開エリア（管理画面・API）
│   ├── app.py
│   ├── multi_agi.py
│   ├── google_search.py
│   ├── failure_learning.py
│   ├── quantum_memory.py
│   └── .env
└── logs/                   # ログディレクトリ
    └── oreza.log
```

### メリット

1. **セキュリティ**: Pythonコードを公開ディレクトリ外に配置
2. **保守性**: 静的ファイルとサーバーコードを分離
3. **攻撃対象削減**: 実行ファイルへの直接アクセスを防止

---

## ファイル権限

### 静的ファイル（HTML, JS, CSS）

```bash
chmod 644 index.html
chmod 644 js/main.js
```

### Pythonファイル

```bash
chmod 644 app.py
chmod 644 multi_agi.py
chmod 644 google_search.py
chmod 644 failure_learning.py
chmod 644 quantum_memory.py
```

### 環境変数ファイル

```bash
chmod 600 .env  # 所有者のみ読み書き可能
```

### ディレクトリ

```bash
chmod 755 www/
chmod 755 js/
chmod 700 secure/  # 非公開エリアは所有者のみアクセス可能
```

---

## 実行権限の削除

**重要**: 静的ファイルやPythonファイルに実行権限(755)は不要です。

```bash
# 不要な実行権限を削除
find /home/orezaai/www -type f -exec chmod 644 {} \;
find /home/orezaai/www -type d -exec chmod 755 {} \;
```

---

## HTTPS確認

### SSL証明書の確認

```bash
# さくらインターネットの管理画面で確認
# コントロールパネル > ドメイン/SSL > SSL証明書
```

### HTTPSアクセステスト

```bash
curl -I https://oreza.com
```

期待される応答:
```
HTTP/2 200
server: nginx
content-type: text/html; charset=utf-8
```

---

## デプロイ方法

### 1. GitHub Actions（推奨）

- `.github/workflows/deploy.yml`を使用
- `main`ブランチへのプッシュで自動デプロイ
- FTPSで安全にアップロード

### 2. 手動デプロイ（緊急時）

```bash
# FTPSクライアント（FileZillaなど）を使用
# ホスト: oreza.com
# プロトコル: FTPS (FTP over TLS)
# ポート: 21
# ユーザー名: orezaai
# パスワード: （GitHub Secretsに保存）
```

---

## デプロイ後の確認

1. **ファイルの存在確認**
   ```bash
   ls -la /home/orezaai/www/
   ```

2. **権限の確認**
   ```bash
   ls -l /home/orezaai/www/index.html
   # 期待: -rw-r--r-- (644)
   ```

3. **HTTPSアクセス確認**
   ```
   https://oreza.com
   ```

4. **不要ファイルの削除確認**
   - `dangerous-clean-slate: true`が効いているか
   - 旧ビルドファイルが残っていないか

---

## セキュリティチェックリスト

- [ ] `.env`ファイルが`.gitignore`に追加されている
- [ ] `.env`ファイルの権限が600になっている
- [ ] 実行権限(755)が不要なファイルから削除されている
- [ ] HTTPSでアクセスできる
- [ ] 公開ディレクトリに機密情報が含まれていない
- [ ] fail2ban, AIDE, auditdが設定されている

---

## トラブルシューティング

### 問題: HTTPSでアクセスできない

**解決策**:
- さくらインターネットの管理画面でSSL証明書を確認
- Let's Encrypt証明書を設定

### 問題: ファイルがアップロードされない

**解決策**:
- GitHub Actionsのログを確認
- FTPSの認証情報を確認
- サーバーのディスク容量を確認

### 問題: 権限エラー

**解決策**:
```bash
# 権限を再設定
chmod 644 /home/orezaai/www/index.html
chmod 755 /home/orezaai/www/
```

---

## 次のステップ

1. セキュリティ要塞化完了を確認
2. GitHub Actionsワークフローを設定
3. `main`ブランチにプッシュ
4. デプロイ完了を確認
5. https://oreza.com でアクセステスト

---

**作成日**: 2025年11月11日  
**バージョン**: 1.0
