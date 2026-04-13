# 🚀 AWS Deployment Guide — Riscos División Rentas

## Where is the database?

```
/Users/luiscarranza/PycharmProjects/FastAPIProject/app.db   (56 KB, SQLite)
```

It is **excluded from git** (`.gitignore`). You have **two options** to get it onto AWS:

| Option | Best for | How |
|--------|----------|-----|
| **A — Upload existing DB** ✅ | All real data, exact state | `./deploy/db_upload.sh` |
| **B — Auto-seed from code** | Fresh start / disaster recovery | Docker entrypoint runs `seed_all.py` automatically on first boot |

**Option A is recommended** — it transfers your exact data (32 units, contracts, bank statements).

```
Internet (port 80/443)
    │
    ▼
EC2 t3.small  (Ubuntu 22.04)
    ├── Nginx  ──────────────────────────────────────────────────────
    │   ├── /           → serves React build  (frontend/dist/)
    │   └── /api/*      → proxies to FastAPI  (localhost:8000)
    │
    └── Docker container
        ├── FastAPI (uvicorn, port 8000)
        └── SQLite DB  (persisted in Docker volume → EBS)
```

**Monthly cost estimate:**
| Resource | Type | ~Cost/month |
|---|---|---|
| EC2 | t3.small (2 vCPU, 2 GB) | ~$15 |
| EBS | 20 GB gp3 | ~$1.60 |
| Data transfer | First 100 GB free | $0 |
| **Total** | | **~$17/month** |

> Use a **t3.micro** (free tier eligible for 12 months) if just testing.

---

## Step 1 — Launch an EC2 instance

1. Go to **AWS Console → EC2 → Launch Instance**
2. Settings:
   - **Name:** `riscos-app`
   - **AMI:** Ubuntu Server 22.04 LTS (64-bit x86)
   - **Instance type:** `t3.small` (or `t3.micro` for free tier)
   - **Key pair:** Create or select one → download the `.pem` file
   - **Security Group — Inbound rules:**
     | Port | Source | Purpose |
     |------|--------|---------|
     | 22   | Your IP only | SSH |
     | 80   | 0.0.0.0/0 | HTTP |
     | 443  | 0.0.0.0/0 | HTTPS (optional) |
   - **Storage:** 20 GB gp3 (default is fine)
3. Click **Launch Instance** → note the **Public IPv4 address**

---

## Step 2 — Fix your SSH key permissions

```bash
chmod 400 ~/Downloads/your-key.pem
# Test connection
ssh -i ~/Downloads/your-key.pem ubuntu@<EC2_PUBLIC_IP>
```

---

## Step 3 — One-time server setup

From your **Mac**, run the setup script (this takes ~5 minutes):

```bash
# From the project root
ssh -i ~/Downloads/your-key.pem ubuntu@<EC2_PUBLIC_IP> 'bash -s' < deploy/setup_ec2.sh
```

This automatically:
- Installs Docker, Nginx, Node.js
- Clones your repo from GitHub
- Builds the React frontend
- Starts the FastAPI backend in Docker
- Configures Nginx to serve everything on port 80
- Creates a systemd service for auto-restart on reboot

---

## Step 4 — Update `docker-compose.prod.yml`

Edit the file and replace the placeholder:
```yaml
ALLOWED_ORIGINS: "http://<EC2_PUBLIC_IP>,https://yourdomain.com"
```

Then redeploy (see Step 6).

---

## Step 5 — Upload your database (real data)

```bash
# Option A — Upload existing app.db (recommended, keeps all real data)
chmod +x deploy/db_upload.sh
./deploy/db_upload.sh -i ~/Downloads/your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Option B — Let Docker auto-seed from seed_all.py (fresh start with base data)
# Nothing to do — happens automatically on first container start
```

---

## Step 6 — Open the app

```
http://<EC2_PUBLIC_IP>
```

---

## Step 7 — Deploying future updates

After pushing changes to `main` on GitHub:

```bash
# From your Mac
./deploy/deploy.sh ubuntu@<EC2_PUBLIC_IP>

# If using a custom SSH key:
ssh-add ~/Downloads/your-key.pem   # add to agent first
./deploy/deploy.sh ubuntu@<EC2_PUBLIC_IP>
```

---

## Step 7 — Add a domain + HTTPS (optional but recommended)

### 7a. Point your domain to EC2
In your DNS provider, add an **A record**: `yourdomain.com → <EC2_PUBLIC_IP>`

### 7b. Install Certbot (free HTTPS via Let's Encrypt)

```bash
ssh ubuntu@<EC2_PUBLIC_IP>
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
# Certbot auto-renews every 90 days
```

### 7c. Update ALLOWED_ORIGINS
```yaml
ALLOWED_ORIGINS: "https://yourdomain.com"
```

---

## Useful commands on the server

```bash
# View API logs
sudo docker compose -f /var/www/riscos/docker-compose.prod.yml logs -f

# Restart API
sudo systemctl restart riscos-api

# Reload Nginx
sudo nginx -t && sudo systemctl reload nginx

# Check what's running on port 80
sudo ss -tlnp | grep :80

# SQLite — access the database directly
sudo docker exec -it riscos-api-1 sqlite3 /data/app.db ".tables"

# Backup the database
sudo docker cp riscos-api-1:/data/app.db ./backup-$(date +%Y%m%d).db
```

---

## Database backup (recommended cron job)

```bash
# Add to crontab on EC2 (crontab -e):
# Backup SQLite daily at 2am and keep 30 days
0 2 * * * docker cp $(docker ps -qf name=api):/data/app.db /home/ubuntu/backups/app-$(date +\%Y\%m\%d).db && find /home/ubuntu/backups -name "*.db" -mtime +30 -delete
```

---

## Environment variables reference

| Variable | Default | Description |
|---|---|---|
| `DB_FILE` | `./app.db` | Path to SQLite database file |
| `UPLOADS_DIR` | `./uploads` | Path to uploaded documents |
| `ALLOWED_ORIGINS` | `""` | Comma-separated extra CORS origins |




