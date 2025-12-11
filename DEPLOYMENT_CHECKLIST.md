# Oreza Simple Chat - デプロイチェックリスト

## 📋 デプロイ前の準備

### ✅ 1. セキュリティ要塞化の確認

- [ ] **fail2ban** が設定されている
- [ ] **AIDE** (Advanced Intrusion Detection Environment) が設定されている
- [ ] **auditd** (監査デーモン) が設定されている
- [ ] ファイアウォール設定が完了している
- [ ] SSH設定が強化されている（鍵認証、ポート変更など）

### ✅ 2. 公開ディレクトリの整合性

- [ ] デプロイ対象が `/home/orezaai/www/` になっている
- [ ] 公開エリアと非公開エリアが分離されている（推奨）
  - 公開: `/home/orezaai/www/` (HTML, JS, CSS)
  - 非公開: `/home/orezaai/secure/` (Python, .env)
- [ ] `.gitignore` が設定されている
- [ ] 不要なファイル（テスト、バックアップ）が除外されている

### ✅ 3. HTTPS・権限確認

- [ ] SSL証明書が設定されている（https://oreza.com）
- [ ] ファイル権限が適切に設定されている:
  - ディレクトリ: 755
  - 静的ファイル (HTML, JS, CSS): 644
  - Pythonファイル: 644
  - .env: 600
- [ ] 不要な実行権限(755)が削除されている
- [ ] `.env` ファイルが `.gitignore` に追加されている

---

## 🚀 デプロイ手順

### Step 1: GitHub Secretsの設定

GitHubリポジトリの Settings > Secrets and variables > Actions で以下を設定:

| Secret名 | 値 | 説明 |
|---------|-----|------|
| `FTP_SERVER` | `oreza.com` | FTPサーバーのホスト名 |
| `FTP_USERNAME` | `orezaai` | FTPユーザー名 |
| `FTP_PASSWORD` | `********` | FTPパスワード |

### Step 2: GitHub Actionsワークフローの確認

`.github/workflows/deploy.yml` が以下の設定になっているか確認:

```yaml
server-dir: /home/orezaai/www/
dangerous-clean-slate: true
protocol: ftps
port: 21
```

### Step 3: mainブランチにプッシュ

```bash
git add .
git commit -m "Deploy Oreza Simple Chat to Sakura"
git push origin main
```

### Step 4: GitHub Actionsの実行確認

1. GitHubリポジトリの **Actions** タブを開く
2. 最新のワークフロー実行を確認
3. **Deploy to Sakura via FTPS** が ✅ になるまで待つ

---

## ✅ デプロイ後の検証

### 1. ファイルの存在確認

```bash
# SSHでサーバーに接続
ssh orezaai@oreza.com

# ファイルの確認
ls -la /home/orezaai/www/
```

期待される出力:
```
-rw-r--r-- 1 orezaai orezaai  xxxxx Nov 11 10:00 index.html
-rw-r--r-- 1 orezaai orezaai  xxxxx Nov 11 10:00 app.py
-rw-r--r-- 1 orezaai orezaai  xxxxx Nov 11 10:00 multi_agi.py
drwxr-xr-x 2 orezaai orezaai   4096 Nov 11 10:00 js
```

### 2. 権限の確認

```bash
# ファイル権限の確認
ls -l /home/orezaai/www/index.html
# 期待: -rw-r--r-- (644)

# ディレクトリ権限の確認
ls -ld /home/orezaai/www/
# 期待: drwxr-xr-x (755)

# 実行権限がないことを確認
find /home/orezaai/www/ -type f -perm /111
# 期待: 何も表示されない（実行権限を持つファイルがない）
```

### 3. HTTPSアクセス確認

```bash
# HTTPSでアクセスできるか確認
curl -I https://oreza.com
```

期待される応答:
```
HTTP/2 200
server: nginx
content-type: text/html; charset=utf-8
```

### 4. ブラウザでアクセス

1. https://oreza.com を開く
2. **Oreza v1** のタイトルが表示されるか確認
3. マイクボタンが表示されるか確認
4. メッセージ入力フィールドが表示されるか確認
5. 検索ボタンが表示されるか確認

### 5. 不要ファイルの削除確認

```bash
# 旧ビルドファイルが残っていないか確認
ls /home/orezaai/www/*_old.* 2>/dev/null
# 期待: "No such file or directory"

ls /home/orezaai/www/*_new.* 2>/dev/null
# 期待: "No such file or directory"

ls /home/ubuntu/oreza-simple-chat/test.html 2>/dev/null
# 期待: "No such file or directory"
```

### 6. 機能テスト

- [ ] メッセージ送信が動作する
- [ ] AI応答が返ってくる
- [ ] Google検索機能が動作する
- [ ] コピーボタンが表示される
- [ ] 音声波形が表示される（音声入力時）
- [ ] レイテンシ表示が更新される

---

## 🔍 トラブルシューティング

### 問題: GitHub Actionsが失敗する

**確認事項**:
1. GitHub Secretsが正しく設定されているか
2. FTPサーバーのホスト名、ユーザー名、パスワードが正しいか
3. サーバーのディスク容量が十分か

**解決策**:
```bash
# GitHub Actionsのログを確認
# Actions > 失敗したワークフロー > ログを確認
```

### 問題: HTTPSでアクセスできない

**確認事項**:
1. SSL証明書が設定されているか
2. ドメインが正しく設定されているか

**解決策**:
```bash
# さくらインターネットの管理画面で確認
# コントロールパネル > ドメイン/SSL > SSL証明書
```

### 問題: ファイルがアップロードされない

**確認事項**:
1. `dangerous-clean-slate: true` が設定されているか
2. `exclude` リストが正しいか

**解決策**:
```yaml
# .github/workflows/deploy.yml を確認
dangerous-clean-slate: true
```

### 問題: 権限エラー

**確認事項**:
1. ファイル権限が644になっているか
2. ディレクトリ権限が755になっているか

**解決策**:
```bash
# 権限を再設定
bash /home/orezaai/www/set_permissions.sh
```

---

## 📊 デプロイ完了チェックリスト

### GitHub Actions

- [ ] ワークフローが ✅ で完了している
- [ ] "Deploy to Sakura via FTPS" ステップが成功している
- [ ] エラーログがない

### サーバー

- [ ] ファイルが `/home/orezaai/www/` に存在する
- [ ] ファイル権限が644になっている
- [ ] ディレクトリ権限が755になっている
- [ ] 不要なファイルが削除されている
- [ ] `.env` ファイルが600になっている（存在する場合）

### アクセス

- [ ] https://oreza.com でアクセスできる
- [ ] SSL証明書が有効
- [ ] ページが正常に表示される
- [ ] すべての機能が動作する

### セキュリティ

- [ ] `.env` ファイルが公開されていない
- [ ] 実行権限が不要なファイルにない
- [ ] fail2ban, AIDE, auditdが動作している
- [ ] ファイアウォールが設定されている

---

## 🎉 デプロイ完了！

すべてのチェックリストが ✅ になったら、デプロイ完了です！

**次のステップ**:
1. ユーザーテストを実施
2. パフォーマンスモニタリング
3. ログの確認
4. バックアップの設定

---

## 📞 サポート

問題が発生した場合は、以下を確認してください:

1. GitHub Actionsのログ
2. サーバーのログ (`/home/orezaai/logs/oreza.log`)
3. ブラウザのコンソールログ
4. `DEPLOYMENT_STRUCTURE.md` - デプロイ構造
5. `set_permissions.sh` - 権限設定スクリプト

---

**作成日**: 2025年11月11日  
**バージョン**: 1.0  
**最終更新**: 2025年11月11日
