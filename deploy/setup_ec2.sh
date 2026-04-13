#!/bin/bash
# =============================================================================
#  EC2 Setup Script — Riscos División Rentas
#  Run ONCE after launching a fresh Ubuntu 22.04 EC2 instance:
#    ssh ubuntu@<EC2_IP> 'bash -s' < deploy/setup_ec2.sh
# =============================================================================
set -e

APP_DIR="/var/www/riscos"
REPO_URL="https://github.com/luis-carranza/estado-cuenta-pagos-rentas.git"

echo "═══════════════════════════════════════════════"
echo "  Riscos División Rentas — EC2 Setup"
echo "═══════════════════════════════════════════════"

# ── 1. System packages ────────────────────────────────────────────────────────
echo "▶ Installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    nginx git curl \
    ca-certificates gnupg lsb-release

# ── 2. Docker ─────────────────────────────────────────────────────────────────
echo "▶ Installing Docker..."
curl -fsSL https://get.docker.com | sudo bash
sudo usermod -aG docker ubuntu
sudo systemctl enable docker

# ── 3. Node.js (for building frontend) ───────────────────────────────────────
echo "▶ Installing Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# ── 4. Clone repo ────────────────────────────────────────────────────────────
echo "▶ Cloning repository..."
sudo mkdir -p $APP_DIR
sudo chown ubuntu:ubuntu $APP_DIR
git clone $REPO_URL $APP_DIR
cd $APP_DIR

# ── 5. Build React frontend ──────────────────────────────────────────────────
echo "▶ Building React frontend..."
cd $APP_DIR/frontend
npm ci --silent
npm run build
# Copy built files to the web root Nginx will serve
sudo mkdir -p $APP_DIR/frontend/dist
echo "  Frontend built at $APP_DIR/frontend/dist"

# ── 6. Docker Compose (start API) ─────────────────────────────────────────────
echo "▶ Starting FastAPI backend via Docker..."
cd $APP_DIR
sudo docker compose -f docker-compose.prod.yml up -d --build

# ── 7. Nginx config ──────────────────────────────────────────────────────────
echo "▶ Configuring Nginx..."
sudo cp $APP_DIR/nginx/nginx.conf /etc/nginx/sites-available/riscos
sudo ln -sf /etc/nginx/sites-available/riscos /etc/nginx/sites-enabled/riscos
sudo rm -f /etc/nginx/sites-enabled/default

# Update the web root path in nginx config
sudo sed -i "s|root /var/www/riscos/frontend;|root $APP_DIR/frontend/dist;|g" \
    /etc/nginx/sites-available/riscos

sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx

# ── 8. Systemd service for auto-restart ──────────────────────────────────────
echo "▶ Creating systemd service..."
sudo tee /etc/systemd/system/riscos-api.service > /dev/null <<EOF
[Unit]
Description=Riscos División Rentas — FastAPI
Requires=docker.service
After=docker.service

[Service]
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/docker compose -f docker-compose.prod.yml up
ExecStop=/usr/bin/docker compose -f docker-compose.prod.yml down
Restart=always
RestartSec=5
User=ubuntu

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable riscos-api

echo ""
echo "═══════════════════════════════════════════════"
echo "  ✅  Setup complete!"
echo ""
echo "  API (internal): http://localhost:8000"
echo "  App (public):   http://$(curl -s ifconfig.me)"
echo ""
echo "  Useful commands:"
echo "    sudo systemctl status riscos-api"
echo "    sudo docker compose -f $APP_DIR/docker-compose.prod.yml logs -f"
echo "    sudo nginx -t && sudo systemctl reload nginx"
echo "═══════════════════════════════════════════════"

