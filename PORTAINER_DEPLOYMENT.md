# 🎯 Portainer Deployment Guide

Complete guide to deploy Spider Price Tracker on Portainer.

---

## Prerequisites

- ✅ Portainer installed and running
- ✅ Docker image pushed to Docker Hub: `raghav0401/spider-app:latest`
- ✅ Your Portainer login credentials

---

## Step-by-Step Deployment

### **1. Login to Portainer**

1. Open browser: `http://your-portainer-ip:9000`
2. Login with your credentials
3. Select your **Environment** (usually "local" or your Docker host)

---

### **2. Create New Stack**

1. In left sidebar, click **"Stacks"**
2. Click **"+ Add stack"** button
3. Enter stack name: `spider-price-tracker`

---

### **3. Add Stack Configuration**

#### **Option A: Web Editor (Recommended)**

1. Select **"Web editor"** tab
2. Copy and paste this compose file:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: spider-postgres
    environment:
      - POSTGRES_DB=spider
      - POSTGRES_USER=spider
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U spider"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - spider-network

  web:
    image: raghav0401/spider-app:latest
    container_name: spider-web
    ports:
      - "5000:5000"
    volumes:
      - spider-data:/app/data
    environment:
      - WEBSITE_USERNAME=${WEBSITE_USERNAME}
      - WEBSITE_PASSWORD=${WEBSITE_PASSWORD}
      - DATABASE_URL=postgresql://spider:${POSTGRES_PASSWORD}@postgres:5432/spider
      - FLASK_HOST=0.0.0.0
      - FLASK_PORT=5000
      - FLASK_DEBUG=False
    restart: unless-stopped
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - spider-network

volumes:
  spider-data:
    driver: local
  postgres-data:
    driver: local

networks:
  spider-network:
    driver: bridge
```

#### **Option B: Upload from Git**

1. Select **"Repository"** tab
2. Enter your Git repository URL
3. Enter compose file path: `docker-compose.portainer.yml`
4. Add credentials if private repo

#### **Option C: Upload File**

1. Select **"Upload"** tab
2. Choose `docker-compose.portainer.yml` from your computer

---

### **4. Configure Environment Variables**

Scroll down to **"Environment variables"** section:

**Method 1: Advanced mode (Recommended)**

Click "Advanced mode" and paste:

```env
WEBSITE_USERNAME=your_breakthrubev_username
WEBSITE_PASSWORD=your_breakthrubev_password
POSTGRES_PASSWORD=your_secure_database_password
```

**Method 2: Simple mode**

Add each variable manually:
| Name | Value |
|------|-------|
| `WEBSITE_USERNAME` | your_breakthrubev_username |
| `WEBSITE_PASSWORD` | your_breakthrubev_password |
| `POSTGRES_PASSWORD` | your_secure_database_password |

**⚠️ IMPORTANT**: Replace these with your actual credentials!

---

### **5. Deploy the Stack**

1. Scroll to bottom
2. Click **"Deploy the stack"** button
3. Wait for deployment (30-60 seconds)

---

### **6. Verify Deployment**

#### **Check Stack Status**

1. Go to **"Stacks"** in sidebar
2. Click on **"spider-price-tracker"**
3. You should see:
   - ✅ **postgres** - Running (healthy)
   - ✅ **web** - Running (healthy)

#### **View Logs**

1. Click on **"web"** container
2. Click **"Logs"** tab
3. Should see: `Running on http://0.0.0.0:5000`

#### **Test Application**

Open browser: `http://your-portainer-host-ip:5000`

You should see the Spider Price Tracker interface.

---

### **7. Run Initial Scrape**

Since the scraper uses a profile, you need to run it manually:

**Option A: Via Portainer Console**

1. Go to **"Containers"** in sidebar
2. Click **"+ Add container"**
3. Configure:
   - **Name**: `spider-scraper-job`
   - **Image**: `raghav0401/spider-app:latest`
   - **Command**: `python run_scraper.py`
   - **Network**: Select `spider-price-tracker_spider-network`
   - **Env variables**: Add same as web service
   - **Volumes**: Map `spider-price-tracker_spider-data` to `/app/data`
   - **Restart policy**: Never
4. Click **"Deploy the container"**
5. Monitor logs for scraping progress

**Option B: Via SSH/Terminal**

SSH to your Portainer host:
```bash
docker run --rm \
  --network spider-price-tracker_spider-network \
  -v spider-price-tracker_spider-data:/app/data \
  -e WEBSITE_USERNAME=your_username \
  -e WEBSITE_PASSWORD=your_password \
  -e DATABASE_URL=postgresql://spider:your_db_password@spider-postgres:5432/spider \
  raghav0401/spider-app:latest \
  python run_scraper.py
```

For infinite scroll (all 7,000+ products):
```bash
docker run --rm \
  --network spider-price-tracker_spider-network \
  -v spider-price-tracker_spider-data:/app/data \
  -e WEBSITE_USERNAME=your_username \
  -e WEBSITE_PASSWORD=your_password \
  -e DATABASE_URL=postgresql://spider:your_db_password@spider-postgres:5432/spider \
  raghav0401/spider-app:latest \
  python run_scraper.py --infinite-scroll
```

---

### **8. Set Up Scheduled Scraping**

#### **Option A: Portainer Webhooks (Easiest)**

1. In your stack, click on **"web"** container
2. Scroll to **"Webhooks"**
3. Click **"Add webhook"**
4. Copy the webhook URL

Then set up a cron job on any machine:
```bash
crontab -e
# Add: Daily at 2 AM
0 2 * * * curl -X POST https://your-portainer-url/api/webhooks/your-webhook-token
```

#### **Option B: Use Portainer Agent**

1. Install Portainer Agent on host
2. Use Portainer's built-in scheduling (Business Edition)

#### **Option C: External Cron**

On your Portainer host:
```bash
crontab -e
# Add this line:
0 2 * * * docker run --rm --network spider-price-tracker_spider-network -v spider-price-tracker_spider-data:/app/data -e WEBSITE_USERNAME=xxx -e WEBSITE_PASSWORD=xxx -e DATABASE_URL=postgresql://spider:xxx@spider-postgres:5432/spider raghav0401/spider-app:latest python run_scraper.py
```

---

### **9. Database Backups**

#### **Manual Backup via Portainer**

1. Go to **"Containers"**
2. Click **"spider-postgres"**
3. Click **"Console"** tab
4. Select `/bin/sh`
5. Run:
```bash
pg_dump -U spider spider > /tmp/backup.sql
```

Then use Portainer's file browser to download.

#### **Automated Backup Script**

On Portainer host:
```bash
# Create backup script
cat > /opt/backup-spider-db.sh << 'SCRIPT'
#!/bin/bash
BACKUP_DIR="/opt/spider-backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

docker exec spider-postgres pg_dump -U spider spider > $BACKUP_DIR/spider_$DATE.sql

# Keep last 7 days
find $BACKUP_DIR -name "spider_*.sql" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/spider_$DATE.sql"
SCRIPT

chmod +x /opt/backup-spider-db.sh

# Schedule daily at 3 AM
crontab -e
# Add: 0 3 * * * /opt/backup-spider-db.sh >> /var/log/spider-backup.log 2>&1
```

---

### **10. Monitoring & Management**

#### **View Container Stats**

1. Go to **"Containers"**
2. See CPU, Memory, Network usage in real-time
3. Click container name for detailed stats

#### **View Logs**

1. Click container name
2. Click **"Logs"** tab
3. Use search, auto-refresh, timestamps

#### **Restart Services**

1. Select container
2. Click **"Restart"** button

#### **Update to Latest Version**

1. Go to **"Stacks"** → **"spider-price-tracker"**
2. Click **"Editor"** tab
3. Click **"Pull and redeploy"**
4. Or manually:
   - Stop stack
   - Pull latest image
   - Redeploy

---

## Portainer Management Commands

### **Using Portainer API**

Get your API token:
```bash
curl -X POST http://your-portainer:9000/api/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"yourpassword"}'
```

List stacks:
```bash
curl -H "X-API-Key: your-api-token" \
  http://your-portainer:9000/api/stacks
```

---

## Troubleshooting

### **Stack won't deploy**

- Check environment variables are set correctly
- Verify image name: `raghav0401/spider-app:latest`
- Check Portainer has internet access to pull images
- Review deployment logs in Portainer

### **PostgreSQL not healthy**

```bash
# Via Portainer Console
docker exec spider-postgres pg_isready -U spider

# Check logs
# In Portainer: Containers → spider-postgres → Logs
```

### **Can't access web interface**

- Check port 5000 is not blocked by firewall
- Verify container is running and healthy
- Check logs for errors
- Try accessing from Portainer host: `curl http://localhost:5000`

### **Scraper fails**

- Verify credentials in environment variables
- Check network connectivity from container
- Review scraper logs for specific errors
- Test manually: Run scraper container with console access

---

## Network Configuration

### **Expose to Internet (Optional)**

#### **1. Use Portainer's Reverse Proxy**

In stack editor, add Traefik labels:
```yaml
  web:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.spider.rule=Host(`spider.yourdomain.com`)"
      - "traefik.http.routers.spider.entrypoints=websecure"
      - "traefik.http.routers.spider.tls.certresolver=letsencrypt"
```

#### **2. Use nginx Proxy Manager**

1. Install nginx Proxy Manager via Portainer
2. Add proxy host:
   - Domain: `spider.yourdomain.com`
   - Forward to: `spider-web:5000`
   - Enable SSL with Let's Encrypt

#### **3. Expose Direct Port**

Change web service port mapping:
```yaml
    ports:
      - "80:5000"  # Expose on port 80
```

---

## Advanced Features

### **Persistent Storage Location**

View volume location:
```bash
docker volume inspect spider-price-tracker_postgres-data
docker volume inspect spider-price-tracker_spider-data
```

### **Resource Limits**

Add to services in stack editor:
```yaml
  web:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 256M
```

### **Multiple Environments**

Create separate stacks for dev/staging/prod:
- `spider-dev`
- `spider-staging`
- `spider-production`

Each with different ports and environment variables.

---

## Quick Reference

### **Access URLs**

- **Portainer**: `http://your-portainer:9000`
- **Spider App**: `http://your-portainer:5000`
- **PostgreSQL**: `your-portainer:5432` (internal only)

### **Common Tasks**

| Task | Steps |
|------|-------|
| View Logs | Containers → Select → Logs |
| Restart Service | Containers → Select → Restart |
| Update Image | Stacks → spider-price-tracker → Pull and redeploy |
| Run Scraper | Create new container with scraper command |
| Backup DB | Console → `pg_dump -U spider spider > backup.sql` |
| Scale Services | Stacks → Edit → Change replicas |

---

## Security Best Practices

1. **Use strong passwords** for POSTGRES_PASSWORD
2. **Don't expose PostgreSQL port** externally
3. **Enable Portainer HTTPS** with valid SSL certificate
4. **Use Portainer RBAC** - create limited user for monitoring
5. **Regular backups** - automate with cron
6. **Update images** regularly for security patches
7. **Monitor logs** for suspicious activity
8. **Use Docker secrets** for sensitive data (Swarm mode)

---

## Support

- **Portainer Docs**: https://docs.portainer.io
- **Docker Hub Image**: https://hub.docker.com/r/raghav0401/spider-app
- **Stack Name**: spider-price-tracker
- **Network**: spider-price-tracker_spider-network
- **Volumes**: 
  - spider-price-tracker_postgres-data
  - spider-price-tracker_spider-data

---

**You're all set!** 🎉

Your Spider Price Tracker is now running on Portainer with:
- ✅ PostgreSQL database
- ✅ Web interface on port 5000
- ✅ Easy management via Portainer UI
- ✅ Health monitoring
- ✅ Automated restarts
