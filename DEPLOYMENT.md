# Production Deployment Guide

This guide explains how to deploy the Spider application on a remote server using Docker.

## Prerequisites

On your remote server:
- Docker Engine installed
- Docker Compose installed
- Git installed (optional, for cloning)

## Deployment Steps

### 1. Transfer Files to Remote Server

You need to transfer these files to your remote server:
- `docker-compose.prod.yml`
- `.env` (with your credentials)

```bash
# Option 1: Using SCP
scp docker-compose.prod.yml .env user@remote-server:/path/to/spider/

# Option 2: Clone the repository
ssh user@remote-server
git clone <your-repo-url>
cd spider
```

### 2. Configure Environment Variables

Create or update `.env` file on the remote server:

```bash
# Required credentials for web scraping
WEBSITE_USERNAME=your_username
WEBSITE_PASSWORD=your_password

# PostgreSQL password (change this!)
POSTGRES_PASSWORD=secure_random_password

# Optional: Database path for SQLite (if not using PostgreSQL)
DATABASE_PATH=data/products.db

# Flask configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
```

**IMPORTANT**: Set a strong password for `POSTGRES_PASSWORD`!

### 3. Start the Services

```bash
# Start web application and PostgreSQL
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### 4. Run the Scraper

The scraper runs on-demand (not continuously):

```bash
# Run scraper once
docker-compose -f docker-compose.prod.yml run --rm scraper

# Run with infinite scroll (collects all 7,000+ products)
docker-compose -f docker-compose.prod.yml run --rm scraper python run_scraper.py --infinite-scroll
```

### 5. Schedule Scraper (Optional)

Set up a cron job to run the scraper periodically:

```bash
# Edit crontab
crontab -e

# Add this line to run scraper daily at 2 AM
0 2 * * * cd /path/to/spider && docker-compose -f docker-compose.prod.yml run --rm scraper
```

### 6. Access the Web Interface

The web application will be available at:
- `http://your-server-ip:5000`

To use a custom domain with HTTPS, set up a reverse proxy (nginx/Caddy).

## Docker Hub Images

The application uses pre-built images from Docker Hub:
- Image: `raghav0401/spider-app:latest`
- Includes: Python, Playwright, Chromium, and all dependencies

## Updating the Application

When a new version is released:

```bash
# Pull latest image
docker-compose -f docker-compose.prod.yml pull

# Restart services
docker-compose -f docker-compose.prod.yml up -d
```

## Database

The production setup includes:

1. **PostgreSQL** (recommended for production)
   - Data persisted in `postgres-data` volume
   - Accessible on port 5432

2. **SQLite** (fallback)
   - Data persisted in `spider-data` volume at `/app/data`

**Note**: The current application uses SQLite. To use PostgreSQL, you'll need to update the database layer code.

## Data Persistence

Data is stored in Docker volumes:
- `postgres-data`: PostgreSQL database
- `spider-data`: SQLite database and other data

### Backup Data

```bash
# Backup PostgreSQL
docker exec spider-postgres pg_dump -U spider spider > backup_$(date +%Y%m%d).sql

# Backup SQLite
docker cp spider-web:/app/data/products.db ./backup_$(date +%Y%m%d).db
```

### Restore Data

```bash
# Restore PostgreSQL
docker exec -i spider-postgres psql -U spider spider < backup.sql

# Restore SQLite
docker cp backup.db spider-web:/app/data/products.db
```

## Troubleshooting

### View logs
```bash
docker-compose -f docker-compose.prod.yml logs web
docker-compose -f docker-compose.prod.yml logs scraper
docker-compose -f docker-compose.prod.yml logs postgres
```

### Restart services
```bash
docker-compose -f docker-compose.prod.yml restart web
```

### Stop all services
```bash
docker-compose -f docker-compose.prod.yml down
```

### Remove everything (including volumes)
```bash
docker-compose -f docker-compose.prod.yml down -v
```

## Security Recommendations

1. **Change default passwords** in `.env`
2. **Restrict port access** - Use firewall to limit port 5000 access
3. **Use HTTPS** - Set up reverse proxy with SSL
4. **Secure .env file**: `chmod 600 .env`
5. **Regular backups** - Schedule automated backups
6. **Update images** - Regularly pull latest images for security patches

## Reverse Proxy Setup (nginx example)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Then use Certbot to add HTTPS:
```bash
sudo certbot --nginx -d your-domain.com
```
