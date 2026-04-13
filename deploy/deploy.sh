#!/bin/bash
# =============================================================================
#  Deploy updates — run from your Mac after pushing to GitHub
#  Usage:  ./deploy/deploy.sh ubuntu@<EC2_IP>
# =============================================================================
set -e

EC2_HOST="${1:?Usage: ./deploy/deploy.sh ubuntu@<EC2_IP_OR_DOMAIN>}"
APP_DIR="/var/www/riscos"

echo "▶ Deploying to $EC2_HOST ..."

ssh "$EC2_HOST" bash << 'REMOTE'
set -e
APP_DIR="/var/www/riscos"
cd "$APP_DIR"

echo "  → Pulling latest code..."
git pull origin main

echo "  → Rebuilding frontend..."
cd frontend
npm ci --silent
npm run build
cd ..

echo "  → Restarting API..."
sudo docker compose -f docker-compose.prod.yml up -d --build

echo "  → Reloading Nginx..."
sudo nginx -t && sudo systemctl reload nginx

echo "  ✅ Deployment complete."
REMOTE

echo "Done! App running at http://$EC2_HOST"

