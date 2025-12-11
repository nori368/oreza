# 🐳 Docker デプロイガイド

Oreza Chat & Shopping PlatformをDockerとVPSにデプロイする詳細な手順

---

## 📋 前提条件

- VPS（Vultr, DigitalOcean, Linode等）
- Docker と Docker Compose がインストール済み
- ドメイン名（オプション）
- OpenAI APIキー
- Google Custom Search APIキーとCSE ID

---

## ステップ1: VPSの準備

### 1.1 VPSを契約

推奨スペック:
- CPU: 1コア以上
- RAM: 1GB以上
- ストレージ: 25GB以上
- OS: Ubuntu 22.04 LTS

推奨プロバイダー:
- **Vultr** ($5/月〜)
- **DigitalOcean** ($6/月〜)
- **Linode** ($5/月〜)

### 1.2 SSHでVPSに接続

```bash
ssh root@<your-vps-ip>
```

### 1.3 システムを更新

```bash
apt update && apt upgrade -y
```

---

## ステップ2: Dockerのインストール

### 2.1 Dockerをインストール

```bash
# 古いバージョンを削除
apt remove docker docker-engine docker.io containerd runc

# 依存関係をインストール
apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# DockerのGPGキーを追加
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Dockerリポジトリを追加
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Dockerをインストール
apt update
apt install -y docker-ce docker-ce-cli containerd.io

# Dockerが起動していることを確認
systemctl status docker
```

### 2.2 Docker Composeをインストール

```bash
# Docker Composeをダウンロード
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 実行権限を付与
chmod +x /usr/local/bin/docker-compose

# バージョンを確認
docker-compose --version
```

---

## ステップ3: プロジェクトファイルのアップロード

### 方法A: SCPでアップロード（ローカルから）

```bash
# ローカルマシンから実行
cd /path/to/oreza_chat
scp -r * root@<your-vps-ip>:/root/oreza_chat/
```

### 方法B: VPS上で直接作成

```bash
# VPS上で実行
mkdir -p /root/oreza_chat
cd /root/oreza_chat

# 必要なディレクトリを作成
mkdir -p images js css data
```

その後、ファイルを1つずつ作成またはアップロード。

---

## ステップ4: 環境変数の設定

### 4.1 .envファイルを作成

```bash
cd /root/oreza_chat
nano .env
```

### 4.2 以下の内容を貼り付け

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-YOUR_ACTUAL_KEY_HERE

# Google Custom Search API Configuration
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY_HERE
GOOGLE_CSE_ID=YOUR_GOOGLE_CSE_ID_HERE

# Authentication
MASTER_ID=oreza-master
MASTER_PASSWORD=VeryStrongPass123!

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### 4.3 保存して終了

```
Ctrl+O (保存)
Enter
Ctrl+X (終了)
```

---

## ステップ5: Dockerイメージのビルド

```bash
cd /root/oreza_chat

# Dockerイメージをビルド
docker-compose build

# ビルドが完了したことを確認
docker images
```

---

## ステップ6: コンテナの起動

```bash
# コンテナをバックグラウンドで起動
docker-compose up -d

# コンテナが起動していることを確認
docker-compose ps

# ログを確認
docker-compose logs -f
```

**Ctrl+C でログ表示を終了**

---

## ステップ7: ファイアウォールの設定

### 7.1 UFWをインストール（まだの場合）

```bash
apt install -y ufw
```

### 7.2 ファイアウォールルールを設定

```bash
# SSHを許可（重要！）
ufw allow 22/tcp

# HTTP/HTTPSを許可
ufw allow 80/tcp
ufw allow 443/tcp

# アプリケーションポート（開発時のみ）
ufw allow 8000/tcp

# ファイアウォールを有効化
ufw enable

# ステータスを確認
ufw status
```

---

## ステップ8: 動作確認

### 8.1 ローカルでテスト

```bash
# VPS上で実行
curl http://localhost:8000/api/health
```

**期待される出力:**
```json
{"status":"ok"}
```

### 8.2 外部からアクセス

ブラウザで以下にアクセス:
```
http://<your-vps-ip>:8000
```

ログインページが表示されれば成功！

---

## ステップ9: Nginxでリバースプロキシを設定（推奨）

### 9.1 Nginxをインストール

```bash
apt install -y nginx
```

### 9.2 Nginx設定ファイルを作成

```bash
nano /etc/nginx/sites-available/oreza
```

### 9.3 以下の内容を貼り付け

```nginx
server {
    listen 80;
    server_name <your-domain.com>;  # ドメインがない場合はVPSのIPアドレス

    client_max_body_size 10M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 9.4 設定を有効化

```bash
# シンボリックリンクを作成
ln -s /etc/nginx/sites-available/oreza /etc/nginx/sites-enabled/

# デフォルト設定を無効化
rm /etc/nginx/sites-enabled/default

# 設定をテスト
nginx -t

# Nginxを再起動
systemctl restart nginx
```

### 9.5 動作確認

ブラウザで以下にアクセス:
```
http://<your-domain.com>
```

または

```
http://<your-vps-ip>
```

---

## ステップ10: SSL証明書の設定（Let's Encrypt）

### 10.1 Certbotをインストール

```bash
apt install -y certbot python3-certbot-nginx
```

### 10.2 SSL証明書を取得

```bash
certbot --nginx -d <your-domain.com>
```

**プロンプトに従って入力:**
- メールアドレス
- 利用規約への同意
- リダイレクト設定（推奨: 2 - Redirect）

### 10.3 自動更新を設定

```bash
# 自動更新のテスト
certbot renew --dry-run

# 自動更新は既に設定されています（systemd timer）
systemctl status certbot.timer
```

### 10.4 動作確認

ブラウザで以下にアクセス:
```
https://<your-domain.com>
```

🔒 HTTPSで接続できれば成功！

---

## 🔧 管理コマンド

### コンテナの管理

```bash
# コンテナの起動
docker-compose up -d

# コンテナの停止
docker-compose down

# コンテナの再起動
docker-compose restart

# ログの確認
docker-compose logs -f

# コンテナの状態確認
docker-compose ps

# コンテナ内でコマンド実行
docker-compose exec oreza-app bash
```

### アプリケーションの更新

```bash
cd /root/oreza_chat

# ファイルを更新（編集またはアップロード）

# コンテナを再ビルド
docker-compose build

# コンテナを再起動
docker-compose up -d
```

### ログの確認

```bash
# アプリケーションログ
docker-compose logs -f oreza-app

# Nginxログ
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 🔄 バックアップ

### データのバックアップ

```bash
# dataディレクトリをバックアップ
tar -czf oreza_backup_$(date +%Y%m%d).tar.gz /root/oreza_chat/data

# リモートサーバーにコピー（オプション）
scp oreza_backup_*.tar.gz user@backup-server:/backups/
```

### 自動バックアップスクリプト

```bash
nano /root/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/root/backups"
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/oreza_backup_$(date +%Y%m%d_%H%M%S).tar.gz /root/oreza_chat/data
# 7日以上古いバックアップを削除
find $BACKUP_DIR -name "oreza_backup_*.tar.gz" -mtime +7 -delete
```

```bash
chmod +x /root/backup.sh

# cronで毎日実行
crontab -e
# 以下を追加
0 2 * * * /root/backup.sh
```

---

## 🔧 トラブルシューティング

### コンテナが起動しない

```bash
# ログを確認
docker-compose logs

# 環境変数を確認
docker-compose exec oreza-app env | grep OPENAI
```

### ポート8000が使用中

```bash
# ポートを使用しているプロセスを確認
lsof -i :8000

# プロセスを停止
kill -9 <PID>
```

### Nginxが起動しない

```bash
# 設定をテスト
nginx -t

# エラーログを確認
tail -f /var/log/nginx/error.log
```

### SSL証明書の取得に失敗

**原因:** ドメインのDNS設定が正しくない

**解決策:**
1. ドメインのAレコードがVPSのIPアドレスを指していることを確認
2. DNS変更が反映されるまで待つ（最大48時間）
3. `nslookup <your-domain.com>` で確認

---

## 📊 監視とメンテナンス

### システムリソースの監視

```bash
# CPU/メモリ使用率
htop

# ディスク使用率
df -h

# Dockerコンテナのリソース使用率
docker stats
```

### ログローテーション

Dockerのログが大きくなりすぎないように設定:

```bash
nano /etc/docker/daemon.json
```

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

```bash
systemctl restart docker
docker-compose up -d
```

---

## 🎯 本番環境のベストプラクティス

### セキュリティ

1. **SSHキー認証を使用**
   ```bash
   # パスワード認証を無効化
   nano /etc/ssh/sshd_config
   # PasswordAuthentication no
   systemctl restart sshd
   ```

2. **定期的なアップデート**
   ```bash
   apt update && apt upgrade -y
   ```

3. **Fail2banをインストール**
   ```bash
   apt install -y fail2ban
   systemctl enable fail2ban
   ```

### パフォーマンス

1. **Nginxのキャッシュを有効化**
2. **CDNを使用**（Cloudflare等）
3. **データベースの最適化**（将来的に追加する場合）

---

## ✅ チェックリスト

デプロイ前に以下を確認:

- [ ] VPSを契約してSSH接続
- [ ] Dockerをインストール
- [ ] プロジェクトファイルをアップロード
- [ ] `.env`ファイルにAPIキーを設定
- [ ] Dockerイメージをビルド
- [ ] コンテナを起動
- [ ] ファイアウォールを設定
- [ ] Nginxをインストールして設定
- [ ] SSL証明書を取得（ドメインがある場合）
- [ ] ブラウザでアクセスして動作確認

---

**デプロイ成功をお祈りします！** 🚀
