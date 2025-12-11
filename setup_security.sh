#!/bin/bash
# Security setup script for Oreza Chat on rental server

set -e

echo "=== Oreza Chat Security Setup ==="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# 1. Update system packages
echo "1. Updating system packages..."
apt-get update
apt-get upgrade -y

# 2. Install required packages
echo "2. Installing required packages..."
apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    nginx \
    certbot \
    python3-certbot-nginx \
    ufw \
    fail2ban

# 3. Configure firewall
echo "3. Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 'Nginx Full'
ufw --force enable

# 4. Configure fail2ban
echo "4. Configuring fail2ban..."
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/oreza-chat-error.log
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# 5. Set up application directory
echo "5. Setting up application directory..."
APP_DIR="/var/www/oreza-chat"
mkdir -p $APP_DIR
mkdir -p $APP_DIR/data

# 6. Set proper permissions
echo "6. Setting proper permissions..."
chown -R www-data:www-data $APP_DIR
chmod 750 $APP_DIR
chmod 700 $APP_DIR/.env 2>/dev/null || true

# 7. Configure nginx
echo "7. Configuring nginx..."
rm -f /etc/nginx/sites-enabled/default

# 8. Enable nginx
echo "8. Enabling nginx..."
systemctl enable nginx
systemctl restart nginx

echo ""
echo "=== Security Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Copy your application files to $APP_DIR"
echo "2. Create .env file with your secrets"
echo "3. Set up SSL certificate: sudo certbot --nginx -d your-domain.com"
echo "4. Copy nginx.conf to /etc/nginx/sites-available/oreza-chat"
echo "5. Create symlink: sudo ln -s /etc/nginx/sites-available/oreza-chat /etc/nginx/sites-enabled/"
echo "6. Copy oreza-chat.service to /etc/systemd/system/"
echo "7. Start the service: sudo systemctl start oreza-chat"
echo ""
