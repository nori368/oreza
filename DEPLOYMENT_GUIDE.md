# Oreza Chat レンタルサーバーデプロイ手順書

## 目次
1. [前提条件](#前提条件)
2. [サーバー準備](#サーバー準備)
3. [セキュリティ設定](#セキュリティ設定)
4. [アプリケーションデプロイ](#アプリケーションデプロイ)
5. [SSL証明書設定](#ssl証明書設定)
6. [動作確認](#動作確認)
7. [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

### サーバー要件
- **OS**: Ubuntu 22.04 LTS 以上
- **メモリ**: 最低 2GB RAM（推奨 4GB）
- **ストレージ**: 最低 10GB
- **Python**: 3.11 以上
- **ドメイン**: SSL証明書用のドメイン名

### 必要な情報
- OpenAI API キー
- Google Search API キー（オプション）
- ドメイン名
- サーバーのIPアドレス

---

## サーバー準備

### 1. サーバーにSSH接続

```bash
ssh root@your-server-ip
```

### 2. 新しいユーザーを作成（rootでの作業を避けるため）

```bash
adduser oreza
usermod -aG sudo oreza
su - oreza
```

### 3. SSH鍵認証を設定（推奨）

ローカルマシンで：
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
ssh-copy-id oreza@your-server-ip
```

---

## セキュリティ設定

### 1. セキュリティスクリプトを実行

```bash
# ファイルをサーバーにアップロード
scp setup_security.sh oreza@your-server-ip:~/

# サーバー上で実行
sudo bash setup_security.sh
```

このスクリプトは以下を自動設定します：
- システムパッケージの更新
- 必要なパッケージのインストール（nginx, certbot, fail2ban等）
- ファイアウォール（ufw）の設定
- fail2banの設定
- アプリケーションディレクトリの作成

### 2. SSH設定の強化

```bash
sudo nano /etc/ssh/sshd_config
```

以下の設定を変更：
```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

SSH再起動：
```bash
sudo systemctl restart sshd
```

---

## アプリケーションデプロイ

### 1. アプリケーションファイルをアップロード

```bash
# ローカルマシンで
cd /path/to/oreza_chat
tar -czf oreza_chat.tar.gz \
    app.py \
    oreza_calendar_v2.py \
    ai_calendar_sync.py \
    multi_agi.py \
    google_search.py \
    index.html \
    calendar_v2.html \
    requirements.txt \
    Dockerfile \
    docker-compose.yml \
    .env.example

# サーバーにアップロード
scp oreza_chat.tar.gz oreza@your-server-ip:~/
```

### 2. サーバー上で展開

```bash
sudo mkdir -p /var/www/oreza-chat
sudo tar -xzf ~/oreza_chat.tar.gz -C /var/www/oreza-chat
sudo chown -R www-data:www-data /var/www/oreza-chat
cd /var/www/oreza-chat
```

### 3. 環境変数を設定

```bash
sudo cp .env.example .env
sudo nano .env
```

`.env`ファイルを編集：
```bash
OPENAI_API_KEY=sk-your-actual-openai-api-key
GOOGLE_SEARCH_API_KEY=your-google-search-api-key
GOOGLE_SEARCH_ENGINE_ID=your-google-search-engine-id
MASTER_ID=oreza-master
MASTER_PASSWORD=YourStrongPasswordHere123!
HOST=127.0.0.1
PORT=8000
```

**重要:** パスワードは必ず変更してください！

権限を設定：
```bash
sudo chmod 600 .env
```

### 4. Python仮想環境を作成

```bash
sudo python3.11 -m venv venv
sudo chown -R www-data:www-data venv
sudo -u www-data venv/bin/pip install -r requirements.txt
```

### 5. systemdサービスを設定

```bash
sudo cp oreza-chat.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable oreza-chat
sudo systemctl start oreza-chat
```

サービス状態を確認：
```bash
sudo systemctl status oreza-chat
```

### 6. Nginx設定

```bash
# nginx.confを編集してドメイン名を設定
sudo nano nginx.conf
# your-domain.com を実際のドメイン名に変更

# 設定ファイルをコピー
sudo cp nginx.conf /etc/nginx/sites-available/oreza-chat
sudo ln -s /etc/nginx/sites-available/oreza-chat /etc/nginx/sites-enabled/

# 設定をテスト
sudo nginx -t

# Nginxを再起動
sudo systemctl restart nginx
```

---

## SSL証明書設定

### Let's Encryptで無料SSL証明書を取得

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

プロンプトに従って：
1. メールアドレスを入力
2. 利用規約に同意
3. HTTPSリダイレクトを有効化

証明書の自動更新を確認：
```bash
sudo certbot renew --dry-run
```

---

## 動作確認

### 1. サービスが起動しているか確認

```bash
sudo systemctl status oreza-chat
sudo systemctl status nginx
```

### 2. ログを確認

```bash
# アプリケーションログ
sudo journalctl -u oreza-chat -f

# Nginxログ
sudo tail -f /var/log/nginx/oreza-chat-access.log
sudo tail -f /var/log/nginx/oreza-chat-error.log
```

### 3. ブラウザでアクセス

```
https://your-domain.com
```

### 4. 機能テスト

1. ログイン画面が表示されることを確認
2. ログイン（MASTER_ID / MASTER_PASSWORD）
3. チャット機能をテスト
4. カレンダー機能をテスト
   - チャットで「今日の午後3時に病院」と入力
   - カレンダーページで予定が表示されることを確認

---

## トラブルシューティング

### アプリケーションが起動しない

```bash
# ログを確認
sudo journalctl -u oreza-chat -n 50

# 手動で起動してエラーを確認
cd /var/www/oreza-chat
sudo -u www-data venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000
```

### Nginxエラー

```bash
# 設定をテスト
sudo nginx -t

# エラーログを確認
sudo tail -f /var/log/nginx/error.log
```

### SSL証明書エラー

```bash
# 証明書の状態を確認
sudo certbot certificates

# 証明書を再取得
sudo certbot --nginx -d your-domain.com --force-renewal
```

### ファイアウォールの問題

```bash
# UFWの状態を確認
sudo ufw status verbose

# ポートを開く
sudo ufw allow 'Nginx Full'
```

### データベース/ストレージの問題

```bash
# ディレクトリの権限を確認
ls -la /var/www/oreza-chat/

# 権限を修正
sudo chown -R www-data:www-data /var/www/oreza-chat/
sudo chmod 750 /var/www/oreza-chat/
```

---

## メンテナンス

### アプリケーションの更新

```bash
# サービスを停止
sudo systemctl stop oreza-chat

# 新しいファイルをアップロード
scp oreza_chat_new.tar.gz oreza@your-server-ip:~/

# バックアップ
sudo cp -r /var/www/oreza-chat /var/www/oreza-chat.backup

# 展開
sudo tar -xzf ~/oreza_chat_new.tar.gz -C /var/www/oreza-chat

# 権限を設定
sudo chown -R www-data:www-data /var/www/oreza-chat

# 依存関係を更新
sudo -u www-data /var/www/oreza-chat/venv/bin/pip install -r /var/www/oreza-chat/requirements.txt

# サービスを再起動
sudo systemctl start oreza-chat
```

### ログのローテーション

```bash
# /etc/logrotate.d/oreza-chat を作成
sudo nano /etc/logrotate.d/oreza-chat
```

内容：
```
/var/log/nginx/oreza-chat-*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

---

## セキュリティチェックリスト

- [ ] SSH鍵認証を設定
- [ ] rootログインを無効化
- [ ] ファイアウォール（ufw）を有効化
- [ ] fail2banを設定
- [ ] SSL証明書を設定
- [ ] .envファイルの権限を600に設定
- [ ] MASTER_PASSWORDを変更
- [ ] 定期的なシステム更新を設定
- [ ] バックアップを設定
- [ ] ログ監視を設定

---

## バックアップ

### 手動バックアップ

```bash
# アプリケーションとデータをバックアップ
sudo tar -czf oreza-chat-backup-$(date +%Y%m%d).tar.gz \
    /var/www/oreza-chat/data \
    /var/www/oreza-chat/.env

# バックアップをローカルにダウンロード
scp oreza@your-server-ip:~/oreza-chat-backup-*.tar.gz ./
```

### 自動バックアップ（cronジョブ）

```bash
sudo crontab -e
```

追加：
```
# 毎日午前3時にバックアップ
0 3 * * * tar -czf /home/oreza/backup/oreza-chat-$(date +\%Y\%m\%d).tar.gz /var/www/oreza-chat/data /var/www/oreza-chat/.env
```

---

## パフォーマンス最適化

### Uvicornワーカー数の調整

```bash
# oreza-chat.serviceを編集
sudo nano /etc/systemd/system/oreza-chat.service
```

ワーカー数を調整（CPU数 x 2 + 1が推奨）：
```
ExecStart=/var/www/oreza-chat/venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000 --workers 4
```

### Nginxキャッシュの設定

nginx.confに追加：
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;

location / {
    proxy_cache my_cache;
    proxy_cache_valid 200 10m;
    # ... 他の設定
}
```

---

## サポート

問題が発生した場合：
1. ログを確認（`sudo journalctl -u oreza-chat -f`）
2. Nginxエラーログを確認（`sudo tail -f /var/log/nginx/oreza-chat-error.log`）
3. サービス状態を確認（`sudo systemctl status oreza-chat`）

---

**デプロイ完了後、必ずセキュリティチェックリストを確認してください！**
