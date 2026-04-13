#!/bin/bash
# =============================================================================
#  db_upload.sh — Upload the local SQLite database to EC2
#
#  Usage:
#    ./deploy/db_upload.sh -i ~/Downloads/your-key.pem ubuntu@<EC2_IP>
#
#  What it does:
#    1. Copies app.db from your Mac to the EC2 Docker volume
#    2. Restarts the API container so it picks up the new database
# =============================================================================
set -e

KEY_FILE=""
EC2_HOST=""

# Parse args
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -i) KEY_FILE="$2"; shift ;;
        *)  EC2_HOST="$1" ;;
    esac
    shift
done

if [[ -z "$EC2_HOST" ]]; then
    echo "Usage: $0 [-i /path/to/key.pem] ubuntu@<EC2_PUBLIC_IP>"
    exit 1
fi

LOCAL_DB="$(dirname "$0")/../app.db"
if [[ ! -f "$LOCAL_DB" ]]; then
    echo "ERROR: app.db not found at $LOCAL_DB"
    exit 1
fi

SSH_OPTS="-o StrictHostKeyChecking=no"
[[ -n "$KEY_FILE" ]] && SSH_OPTS="$SSH_OPTS -i $KEY_FILE"
SCP_OPTS="$SSH_OPTS"

echo "═════════════════════════════════════════════"
echo "  Uploading app.db → $EC2_HOST"
echo "  Size: $(du -sh "$LOCAL_DB" | cut -f1)"
echo "═════════════════════════════════════════════"

# Step 1: copy DB to home dir on EC2
scp $SCP_OPTS "$LOCAL_DB" "${EC2_HOST}:/home/ubuntu/app.db"

# Step 2: move it into the Docker volume (requires root)
ssh $SSH_OPTS "$EC2_HOST" bash << 'REMOTE'
  set -e
  echo "  → Copying into Docker volume..."
  CONTAINER=$(sudo docker ps --filter "name=api" -q | head -1)
  if [[ -n "$CONTAINER" ]]; then
      sudo docker cp /home/ubuntu/app.db "${CONTAINER}:/data/app.db"
      echo "  → Restarting API container..."
      sudo docker restart "$CONTAINER"
  else
      # Fallback: copy to named volume mount path
      VOLUME_PATH=$(sudo docker volume inspect riscos_db_data --format '{{.Mountpoint}}' 2>/dev/null || echo "")
      if [[ -n "$VOLUME_PATH" ]]; then
          sudo cp /home/ubuntu/app.db "${VOLUME_PATH}/app.db"
          echo "  → Copied to volume: $VOLUME_PATH"
          sudo docker compose -f /var/www/riscos/docker-compose.prod.yml restart
      else
          echo "  WARNING: No running container found. DB saved to /home/ubuntu/app.db"
          echo "  Run manually: sudo docker cp /home/ubuntu/app.db <container_id>:/data/app.db"
      fi
  fi
  rm -f /home/ubuntu/app.db
  echo "  ✅ Database uploaded successfully."
REMOTE

echo ""
echo "✅ Done. The app is using your local database."
echo "   Open: http://$EC2_HOST"

