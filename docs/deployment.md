# Deployment Guide

> How to deploy AI Wellness Platform to a production VPS.

---

## Architecture

```
                         Cloudflare DNS
                              │
            wellness.thomasyeung.dev  api.wellness.thomasyeung.dev
                              │
                         ┌────┴────┐
                         │  nginx  │  (SSL termination, rate limiting)
                         │ :443    │
                         └────┬────┘
                    ┌─────────┴──────────┐
                    ▼                    ▼
            ┌──────────────┐   ┌──────────────┐
            │  Streamlit   │   │   FastAPI    │
            │  :8501       │   │  :8000       │
            │              │   │              │
            │  pages/      │   │  /api/v1/*   │
            └──────────────┘   └──────┬───────┘
                                      │
                                 ┌────┴────┐
                                 │ SQLite  │
                                 │ Volume  │
                                 └─────────┘
```

---

## Prerequisites

- A VPS running **Ubuntu 24.04** (tested: Hetzner CX22, $5/month)
- A domain name pointing to the VPS IP (e.g., `wellness.thomasyeung.dev`)
- Docker and Docker Compose installed on the VPS

---

## Step 1: DNS Setup

Add A records in your DNS provider (Cloudflare recommended):

| Type | Name | Value |
|------|------|-------|
| A | `wellness` | `<VPS-IP-ADDRESS>` |
| A | `api` | `<VPS-IP-ADDRESS>` |

Set Cloudflare to **DNS Only** (grey cloud) initially, then switch to **Proxied** (orange cloud) after SSL is working.

Wait 5-15 minutes for DNS propagation.

```bash
dig wellness.thomasyeung.dev +short
# Should return your VPS IP
```

---

## Step 2: VPS Initial Setup

```bash
# SSH into your VPS
ssh root@<vps-ip>

# Update system
apt update && apt upgrade -y

# Install Docker
apt install docker.io docker-compose-v2 -y

# Verify
docker --version
docker compose version

# Install nginx (for Let's Encrypt standalone challenge)
apt install nginx certbot python3-certbot-nginx -y

# Configure firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Verify
ufw status
```

---

## Step 3: Clone and Configure

```bash
# Clone repository
cd /opt
git clone https://github.com/thomasyeung79/health-risk-system.git
cd health-risk-system

# Create production environment file
cp .env.production.example .env.production

# Edit and fill in secrets
nano .env.production
```

Required changes in `.env.production`:

| Variable | Value |
|----------|-------|
| `JWT_SECRET` | Run `python3 -c "import secrets; print(secrets.token_hex(32))"` and paste output |
| `CORS_ORIGINS` | `https://wellness.thomasyeung.dev,https://api.wellness.thomasyeung.dev` |
| `DEBUG` | `false` |
| `DEEPSEEK_API_KEY` | Your DeepSeek key, or leave blank for local fallback |

---

## Step 4: SSL Certificate

```bash
# Obtain SSL certificate via Let's Encrypt
certbot certonly --nginx \
    -d wellness.thomasyeung.dev \
    -d api.wellness.thomasyeung.dev

# This creates certificates at:
#   /etc/letsencrypt/live/wellness.thomasyeung.dev/fullchain.pem
#   /etc/letsencrypt/live/wellness.thomasyeung.dev/privkey.pem

# Test auto-renewal
certbot renew --dry-run
```

---

## Step 5: Launch with Docker Compose

```bash
# Build and start all services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Check status
docker compose ps
docker compose logs --tail=30

# Wait for health checks (30 seconds)
sleep 30
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Expected output:

```
NAMES                    STATUS
ai-wellness-nginx        Up 1 minute
ai-wellness-frontend     Up 1 minute (healthy)
ai-wellness-backend      Up 1 minute (healthy)
```

---

## Step 6: Verify Deployment

```bash
# Backend API health
curl -s https://api.wellness.thomasyeung.dev/health
# Expected: {"status":"ok","version":"0.1.0"}

# Swagger docs
curl -s -o /dev/null -w "%{http_code}" https://api.wellness.thomasyeung.dev/docs
# Expected: 200

# Frontend
curl -s -o /dev/null -w "%{http_code}" https://wellness.thomasyeung.dev
# Expected: 200

# Full user journey
# 1. Register
curl -s -X POST https://api.wellness.thomasyeung.dev/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"username":"demo","password":"Demo123456"}'
# Expected: 201

# 2. Login
curl -s -X POST https://api.wellness.thomasyeung.dev/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"demo","password":"Demo123456"}'
# Expected: 200 + JWT tokens
```

---

## Step 7: Set Up Automated Backups

```bash
# Make backup script executable
chmod +x scripts/backup_sqlite.sh

# Add to crontab (runs daily at 3 AM)
(crontab -l 2>/dev/null; echo "0 3 * * * /opt/health-risk-system/scripts/backup_sqlite.sh") | crontab -

# Test backup
./scripts/backup_sqlite.sh

# Verify backup file
ls -la backups/
```

---

## Step 8: Production Validation Checklist

- [ ] `https://wellness.thomasyeung.dev` loads without errors
- [ ] `https://api.wellness.thomasyeung.dev/health` returns 200
- [ ] Register a new account works
- [ ] Login works and JWT tokens are returned
- [ ] Health Check form submits successfully
- [ ] Emotion Analysis generates results
- [ ] History page shows records
- [ ] Final Report generates (with DeepSeek or local fallback)
- [ ] Logout works (refresh token revoked)
- [ ] Mobile browser renders correctly
- [ ] SSL certificate is valid (`curl -vI https://...` returns no errors)
- [ ] Backup script runs without errors

---

## Step 9: Post-Deployment

```bash
# Monitor logs
docker compose logs --tail=50 -f

# Restart a single service
docker compose restart backend

# Update after code changes
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Full stop and cleanup
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
```

---

## Shutting Down

```bash
# Graceful shutdown
docker compose down

# Remove all data (including SQLite database)
docker compose down -v

# Remove old images
docker image prune -a
```

---

## Troubleshooting

### `502 Bad Gateway` from nginx

```bash
# Check if backend is running
docker ps | grep ai-wellness

# Check backend logs
docker compose logs backend --tail=20

# Restart nginx
docker compose restart nginx
```

### SQLite `database is locked` errors

The SQLite database uses a Docker volume. If multiple users access simultaneously:

```bash
# Check SQLite file permissions
docker compose exec backend ls -la /app/backend/data/

# Restart backend to clear locks
docker compose restart backend
```

### SSL certificate expiry

Let's Encrypt certificates expire after 90 days. Auto-renewal is handled by `certbot renew` via systemd timer:

```bash
# Check expiry date
openssl x509 -in /etc/letsencrypt/live/wellness.thomasyeung.dev/fullchain.pem -noout -enddate

# Test renewal
certbot renew --dry-run
```

---

## Appendix: Quick-Start Command Sequence

```bash
# Copy-paste this entire block on a fresh Ubuntu 24.04 VPS:

apt update && apt upgrade -y
apt install docker.io docker-compose-v2 nginx certbot python3-certbot-nginx ufw -y
ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp && ufw enable

git clone https://github.com/thomasyeung79/health-risk-system.git /opt/health-risk-system
cd /opt/health-risk-system
cp .env.production.example .env.production
# EDIT .env.production (set JWT_SECRET, CORS_ORIGINS, DEBUG=false)

certbot certonly --nginx -d wellness.thomasyeung.dev -d api.wellness.thomasyeung.dev
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
