#!/bin/bash

# Production Server Setup Script for 135.181.106.12
# Run this ONCE on your production server

echo "🚀 Setting up Morphik on production server..."

# 1. Clone repository
cd /opt
sudo rm -rf morphik
sudo git clone https://github.com/We-are-Humans-Corp/Morphik_local.git morphik
cd morphik

# 2. Create production environment file
sudo tee .env.production << EOF
# Database
DATABASE_URL=postgresql://morphik:morphik_prod_2024@postgres:5432/morphik
POSTGRES_USER=morphik
POSTGRES_PASSWORD=morphik_prod_2024
POSTGRES_DB=morphik

# API Keys
ANTHROPIC_API_KEY=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

# Security
JWT_SECRET_KEY=$(openssl rand -base64 32)
SESSION_SECRET_KEY=$(openssl rand -base64 32)

# Mode
MODE=self_hosted
EOF

# 3. Create auto-deploy script
sudo tee /opt/morphik/deploy.sh << 'DEPLOY_SCRIPT'
#!/bin/bash
cd /opt/morphik

echo "📥 Pulling latest from GitHub..."
git pull origin main

echo "🔄 Using production environment..."
cp .env.production .env

echo "🛑 Stopping old containers..."
docker-compose -f docker-compose-official.yml down

echo "🐳 Starting new containers..."
docker-compose -f docker-compose-official.yml up -d

echo "⏳ Waiting for services..."
sleep 30

echo "🔄 Running migrations..."
docker exec morphik-morphik-1 python -m alembic upgrade head
docker exec morphik-morphik-1 psql -U morphik -d morphik -f /app/migrations/add_users_table.sql

echo "✅ Deployment complete!"
echo "🌐 Access at: http://135.181.106.12:8000 (API) and http://135.181.106.12:3000 (UI)"
DEPLOY_SCRIPT

sudo chmod +x /opt/morphik/deploy.sh

# 4. Create webhook service
sudo tee /etc/webhook.conf << EOF
[
  {
    "id": "morphik-deploy",
    "execute-command": "/opt/morphik/deploy.sh",
    "command-working-directory": "/opt/morphik",
    "response-message": "Deployment started",
    "trigger-rule": {
      "match": {
        "type": "payload-hash-sha1",
        "secret": "morphik-webhook-secret-2024",
        "parameter": {
          "source": "header",
          "name": "X-Hub-Signature"
        }
      }
    }
  }
]
EOF

# 5. Install webhook if not installed
if ! command -v webhook &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y webhook
fi

# 6. Create webhook systemd service
sudo tee /etc/systemd/system/webhook.service << EOF
[Unit]
Description=Webhook for Morphik Auto-Deploy
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/webhook -hooks /etc/webhook.conf -verbose -port 9000
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 7. Start webhook service
sudo systemctl daemon-reload
sudo systemctl enable webhook
sudo systemctl restart webhook

# 8. Run initial deployment
sudo /opt/morphik/deploy.sh

echo "✅ Server setup complete!"
echo "🔗 Add webhook to GitHub: http://135.181.106.12:9000/hooks/morphik-deploy"
echo "🔑 Webhook secret: morphik-webhook-secret-2024"