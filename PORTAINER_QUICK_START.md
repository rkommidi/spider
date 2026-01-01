# 🚀 Portainer Quick Start - Spider Price Tracker

**5-Minute Deployment Guide**

---

## 1️⃣ Login to Portainer
```
http://your-portainer-ip:9000
```

---

## 2️⃣ Create Stack

1. **Stacks** → **+ Add stack**
2. **Name**: `spider-price-tracker`
3. **Web editor** → Paste this:

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
  postgres-data:

networks:
  spider-network:
```

---

## 3️⃣ Set Environment Variables

Scroll down → **Environment variables** → **Advanced mode**

```env
WEBSITE_USERNAME=your_breakthrubev_username
WEBSITE_PASSWORD=your_breakthrubev_password
POSTGRES_PASSWORD=YOUR_SECURE_DB_PASSWORD
```

**⚠️ Change these values!**

---

## 4️⃣ Deploy

Click **"Deploy the stack"** → Wait 30 seconds

---

## 5️⃣ Access App

```
http://your-portainer-ip:5000
```

---

## 6️⃣ Run First Scrape

**SSH to Portainer host and run:**

```bash
docker run --rm \
  --network spider-price-tracker_spider-network \
  -v spider-price-tracker_spider-data:/app/data \
  -e WEBSITE_USERNAME=your_username \
  -e WEBSITE_PASSWORD=your_password \
  -e DATABASE_URL=postgresql://spider:your_db_pass@spider-postgres:5432/spider \
  raghav0401/spider-app:latest \
  python run_scraper.py
```

**For all 7,000+ products (6-10 hours):**
```bash
docker run --rm \
  --network spider-price-tracker_spider-network \
  -v spider-price-tracker_spider-data:/app/data \
  -e WEBSITE_USERNAME=your_username \
  -e WEBSITE_PASSWORD=your_password \
  -e DATABASE_URL=postgresql://spider:your_db_pass@spider-postgres:5432/spider \
  raghav0401/spider-app:latest \
  python run_scraper.py --infinite-scroll
```

---

## ✅ Done!

You now have:
- ✅ Web app running on port 5000
- ✅ PostgreSQL database
- ✅ Auto-restart enabled
- ✅ Health monitoring

---

## Common Tasks

### View Logs
Portainer → **Containers** → **spider-web** → **Logs**

### Restart Service
Portainer → **Containers** → Select → **Restart**

### Backup Database
```bash
docker exec spider-postgres pg_dump -U spider spider > backup.sql
```

### Update to Latest
Portainer → **Stacks** → **spider-price-tracker** → **Pull and redeploy**

### Schedule Daily Scraping
On Portainer host, add to crontab:
```bash
0 2 * * * docker run --rm --network spider-price-tracker_spider-network -v spider-price-tracker_spider-data:/app/data -e WEBSITE_USERNAME=xxx -e WEBSITE_PASSWORD=xxx -e DATABASE_URL=postgresql://spider:xxx@spider-postgres:5432/spider raghav0401/spider-app:latest python run_scraper.py
```

---

## 📚 Full Guide

See `PORTAINER_DEPLOYMENT.md` for detailed instructions.

---

**Docker Image**: `raghav0401/spider-app:latest`  
**PostgreSQL**: Version 16 Alpine  
**Default Port**: 5000
