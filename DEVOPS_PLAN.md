# DevOps Transformation Plan
## Spider Price Tracker - Containerization & CI/CD

---

## 🎯 Project Overview

**Current State:** Monolithic Flask app with SQLite
**Target State:** Microservices architecture with PostgreSQL, full CI/CD pipeline
**Deployment Target:** Portainer on NAS (dev + prod environments)

---

## 📋 Phase-by-Phase Implementation Plan

### **PHASE 1: Project Containerization** (Week 1)
*Goal: Get all services running in Docker containers locally*

#### 1.1 Directory Structure Setup
```
spider/
├── docker/
│   ├── flask/
│   │   └── Dockerfile
│   ├── scraper/
│   │   └── Dockerfile
│   ├── postgres/
│   │   ├── Dockerfile
│   │   └── init.sql
│   └── jenkins/
│       └── Dockerfile
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── .dockerignore
├── helm/
│   └── spider-chart/
│       ├── Chart.yaml
│       ├── values.dev.yaml
│       ├── values.prod.yaml
│       └── templates/
└── jenkins/
    ├── Jenkinsfile
    └── pipelines/
```

#### 1.2 Service Breakdown
1. **Flask Web App** - Read-only web interface
2. **Scraper Service** - Scheduled job (cron-based)
3. **PostgreSQL** - Shared database
4. **Jenkins** - CI/CD orchestration
5. **Nginx** (optional) - Reverse proxy for Flask

#### 1.3 Create Dockerfiles

**Flask App Dockerfile:**
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .
COPY templates/ templates/
COPY static/ static/
COPY database.py .

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

# Run app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
```

**Scraper Dockerfile:**
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy scraper code
COPY run_scraper.py .
COPY scraper.py .
COPY database.py .

# Run scraper (can be overridden by cron or manual trigger)
CMD ["python", "run_scraper.py"]
```

#### 1.4 Docker Compose for Local Development

**docker-compose.dev.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: spider-db-dev
    environment:
      POSTGRES_DB: spider_dev
      POSTGRES_USER: spider
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data_dev:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U spider"]
      interval: 10s
      timeout: 5s
      retries: 5

  flask:
    build:
      context: .
      dockerfile: docker/flask/Dockerfile
    container_name: spider-flask-dev
    environment:
      FLASK_ENV: development
      FLASK_DEBUG: "True"
      DATABASE_URL: postgresql://spider:${DB_PASSWORD}@postgres:5432/spider_dev
      FLASK_HOST: 0.0.0.0
      FLASK_PORT: 5000
    ports:
      - "5000:5000"
    volumes:
      - ./app.py:/app/app.py
      - ./templates:/app/templates
      - ./static:/app/static
      - ./database.py:/app/database.py
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

  scraper:
    build:
      context: .
      dockerfile: docker/scraper/Dockerfile
    container_name: spider-scraper-dev
    environment:
      DATABASE_URL: postgresql://spider:${DB_PASSWORD}@postgres:5432/spider_dev
      WEBSITE_USERNAME: ${WEBSITE_USERNAME}
      WEBSITE_PASSWORD: ${WEBSITE_PASSWORD}
    volumes:
      - scraper_screenshots:/app/screenshots
    depends_on:
      postgres:
        condition: service_healthy
    restart: "no"  # Manual trigger or cron

volumes:
  postgres_data_dev:
  scraper_screenshots:
```

---

### **PHASE 2: Database Migration** (Week 1-2)
*Goal: Migrate from SQLite to PostgreSQL*

#### 2.1 Create Migration Script

**migrations/migrate_sqlite_to_postgres.py:**
```python
#!/usr/bin/env python3
"""Migrate data from SQLite to PostgreSQL"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_batch
import os

def migrate():
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('data/products.db')
    sqlite_conn.row_factory = sqlite3.Row

    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(os.getenv('DATABASE_URL'))

    # Migrate products table
    print("Migrating products...")
    sqlite_cur = sqlite_conn.execute("SELECT * FROM products")
    products = [dict(row) for row in sqlite_cur.fetchall()]

    pg_cur = pg_conn.cursor()
    execute_batch(pg_cur, """
        INSERT INTO products (id, name, url, created_at, ...)
        VALUES (%(id)s, %(name)s, %(url)s, %(created_at)s, ...)
        ON CONFLICT (id) DO NOTHING
    """, products)

    # Migrate price_history table
    print("Migrating price history...")
    # ... similar pattern

    pg_conn.commit()
    print("Migration complete!")

if __name__ == '__main__':
    migrate()
```

#### 2.2 Update database.py for PostgreSQL
- Add PostgreSQL connection string support
- Update queries for PostgreSQL compatibility
- Handle serial IDs vs autoincrement
- Add connection pooling

---

### **PHASE 3: CI/CD Pipeline Setup** (Week 2-3)
*Goal: Automated builds and deployments*

#### 3.1 Jenkins Setup

**docker-compose.jenkins.yml:**
```yaml
version: '3.8'

services:
  jenkins:
    image: jenkins/jenkins:lts
    container_name: spider-jenkins
    privileged: true
    user: root
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
      - ./jenkins:/jenkins_config
    environment:
      - DOCKER_HOST=unix:///var/run/docker.sock

volumes:
  jenkins_home:
```

#### 3.2 Jenkins Pipeline (Jenkinsfile)

```groovy
pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'your-dockerhub-username'
        DOCKER_CREDENTIALS = credentials('dockerhub-credentials')
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        GIT_COMMIT_SHORT = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
    }

    parameters {
        choice(name: 'ENVIRONMENT', choices: ['dev', 'prod'], description: 'Deployment environment')
        booleanParam(name: 'SKIP_TESTS', defaultValue: false, description: 'Skip tests')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Images') {
            parallel {
                stage('Build Flask') {
                    steps {
                        script {
                            docker.build("${DOCKER_REGISTRY}/spider-flask:${IMAGE_TAG}",
                                        "-f docker/flask/Dockerfile .")
                            docker.build("${DOCKER_REGISTRY}/spider-flask:latest",
                                        "-f docker/flask/Dockerfile .")
                        }
                    }
                }
                stage('Build Scraper') {
                    steps {
                        script {
                            docker.build("${DOCKER_REGISTRY}/spider-scraper:${IMAGE_TAG}",
                                        "-f docker/scraper/Dockerfile .")
                            docker.build("${DOCKER_REGISTRY}/spider-scraper:latest",
                                        "-f docker/scraper/Dockerfile .")
                        }
                    }
                }
            }
        }

        stage('Test') {
            when {
                expression { params.SKIP_TESTS == false }
            }
            steps {
                sh 'docker-compose -f docker-compose.test.yml up --abort-on-container-exit'
            }
        }

        stage('Push to Registry') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials') {
                        sh """
                            docker push ${DOCKER_REGISTRY}/spider-flask:${IMAGE_TAG}
                            docker push ${DOCKER_REGISTRY}/spider-flask:latest
                            docker push ${DOCKER_REGISTRY}/spider-scraper:${IMAGE_TAG}
                            docker push ${DOCKER_REGISTRY}/spider-scraper:latest
                        """
                    }
                }
            }
        }

        stage('Deploy to Portainer') {
            steps {
                script {
                    def stackName = params.ENVIRONMENT == 'prod' ? 'spider-prod' : 'spider-dev'
                    def composeFile = params.ENVIRONMENT == 'prod' ?
                                     'docker-compose.prod.yml' : 'docker-compose.dev.yml'

                    // Deploy via Portainer API
                    sh """
                        curl -X POST '${PORTAINER_URL}/api/stacks/${stackName}/git/redeploy' \
                          -H 'X-API-Key: ${PORTAINER_API_KEY}' \
                          -H 'Content-Type: application/json' \
                          -d '{
                            "repositoryAuthentication": false,
                            "env": [
                              {"name": "IMAGE_TAG", "value": "${IMAGE_TAG}"}
                            ]
                          }'
                    """
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    def appUrl = params.ENVIRONMENT == 'prod' ?
                                'https://spider.yourdomain.com' :
                                'http://spider-dev.local:5000'

                    retry(3) {
                        sleep(10)
                        sh "curl -f ${appUrl}/health || exit 1"
                    }
                }
            }
        }
    }

    post {
        success {
            echo "✅ Deployment successful to ${params.ENVIRONMENT}!"
        }
        failure {
            echo "❌ Deployment failed!"
        }
        always {
            cleanWs()
        }
    }
}
```

#### 3.3 Portainer Stack Configuration

**For dev environment:**
Create stack in Portainer UI with:
- Stack name: `spider-dev`
- Git repository: Your repo URL
- Compose file path: `docker-compose.dev.yml`
- Environment variables

**For prod environment:**
- Stack name: `spider-prod`
- Compose file path: `docker-compose.prod.yml`

---

### **PHASE 4: Environment Management** (Week 3)
*Goal: Proper dev/prod separation*

#### 4.1 Environment Variables

**.env.dev:**
```bash
# Database
DB_PASSWORD=dev_password_change_me
DATABASE_URL=postgresql://spider:dev_password_change_me@postgres:5432/spider_dev

# Flask
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Scraper
WEBSITE_USERNAME=your_username
WEBSITE_PASSWORD=your_password

# Portainer
PORTAINER_URL=http://your-nas-ip:9000
```

**.env.prod:**
```bash
# Database (use secrets management!)
DB_PASSWORD=${PROD_DB_PASSWORD}
DATABASE_URL=postgresql://spider:${PROD_DB_PASSWORD}@postgres:5432/spider_prod

# Flask
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Scraper
WEBSITE_USERNAME=${PROD_USERNAME}
WEBSITE_PASSWORD=${PROD_PASSWORD}
```

#### 4.2 Secrets Management

**Using Docker Secrets (recommended for production):**
```yaml
# docker-compose.prod.yml
services:
  flask:
    secrets:
      - db_password
      - website_credentials
    environment:
      DATABASE_PASSWORD_FILE: /run/secrets/db_password

secrets:
  db_password:
    external: true
  website_credentials:
    external: true
```

---

### **PHASE 5: Helm Charts (Optional)** (Week 4)
*Goal: Kubernetes-ready deployment*

#### 5.1 Helm Chart Structure

**helm/spider-chart/Chart.yaml:**
```yaml
apiVersion: v2
name: spider
description: Price tracking application
type: application
version: 1.0.0
appVersion: "1.0.0"
```

**helm/spider-chart/values.dev.yaml:**
```yaml
environment: dev

flask:
  image:
    repository: your-dockerhub/spider-flask
    tag: latest
  replicas: 1
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"

scraper:
  image:
    repository: your-dockerhub/spider-scraper
    tag: latest
  schedule: "0 2 * * *"  # Daily at 2 AM

postgres:
  enabled: true
  auth:
    database: spider_dev
    username: spider
  persistence:
    size: 10Gi
```

---

## 🔧 Implementation Checklist

### Week 1: Containerization
- [ ] Create directory structure
- [ ] Write Dockerfiles for Flask and Scraper
- [ ] Create docker-compose.dev.yml
- [ ] Test local container builds
- [ ] Update requirements.txt with gunicorn, psycopg2
- [ ] Add health check endpoints to Flask

### Week 2: Database Migration
- [ ] Set up PostgreSQL container
- [ ] Update database.py for PostgreSQL compatibility
- [ ] Write migration script
- [ ] Test migration with sample data
- [ ] Update connection pooling
- [ ] Create database backup strategy

### Week 3: Jenkins & CI/CD
- [ ] Set up Jenkins container
- [ ] Install required Jenkins plugins
  - Docker Pipeline
  - Git
  - Credentials Binding
  - Portainer
- [ ] Configure Docker Hub credentials in Jenkins
- [ ] Configure Portainer API credentials
- [ ] Create Jenkinsfile
- [ ] Test CI pipeline (build + push)
- [ ] Test CD pipeline (deploy to dev)
- [ ] Set up prod environment

### Week 4: Production Hardening
- [ ] Implement secrets management
- [ ] Add SSL/TLS certificates
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure log aggregation (ELK stack)
- [ ] Add backup automation
- [ ] Document runbooks
- [ ] Load testing
- [ ] Disaster recovery plan

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         DEVELOPER                            │
└───────────────────────┬─────────────────────────────────────┘
                        │ git push
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                      GitHub Repository                       │
└───────────────────────┬─────────────────────────────────────┘
                        │ webhook
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Jenkins (CI/CD)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Build      │→ │    Test      │→ │  Push to     │      │
│  │   Containers │  │   Containers │  │  Docker Hub  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└───────────────────────┬─────────────────────────────────────┘
                        │ deploy via Portainer API
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Portainer (on NAS Device)                       │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              DEV Environment                           │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │ │
│  │  │  Flask   │  │ Scraper  │  │Postgres  │            │ │
│  │  │   :5001  │  │ (cron)   │  │  :5432   │            │ │
│  │  └──────────┘  └──────────┘  └──────────┘            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              PROD Environment                          │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │ │
│  │  │  Flask   │  │ Scraper  │  │Postgres  │            │ │
│  │  │   :5000  │  │ (cron)   │  │  :5433   │            │ │
│  │  └──────────┘  └──────────┘  └──────────┘            │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Monitoring & Observability

### Metrics to Track
- Flask app response times
- Scraper success/failure rate
- Database connection pool usage
- Container resource usage (CPU, RAM)
- Disk usage growth

### Recommended Tools
1. **Prometheus** - Metrics collection
2. **Grafana** - Visualization
3. **ELK Stack** - Log aggregation
4. **Sentry** - Error tracking

---

## 🔒 Security Considerations

1. **Secrets Management**
   - Never commit credentials to Git
   - Use Docker secrets or Vault for production
   - Rotate credentials regularly

2. **Network Security**
   - Use internal Docker networks
   - Expose only necessary ports
   - Implement rate limiting on Flask

3. **Container Security**
   - Use non-root users in Dockerfiles
   - Scan images for vulnerabilities
   - Keep base images updated

4. **Database Security**
   - Enable SSL connections
   - Regular backups
   - Restricted user permissions

---

## 🚀 Deployment Workflow

### Development Workflow
```
1. Developer commits code → GitHub
2. Jenkins detects webhook
3. Runs CI pipeline (build + test)
4. Pushes images to Docker Hub
5. Auto-deploys to dev environment
6. Runs health checks
```

### Production Workflow
```
1. Manual trigger in Jenkins (or tag-based)
2. Runs full test suite
3. Builds production images
4. Pushes to Docker Hub with version tags
5. Manual approval required
6. Deploys to prod environment
7. Runs health checks
8. Sends notification (Slack/Email)
```

---

## 📝 Next Steps

1. **Review this plan** with your senior DevOps/SRE engineer
2. **Set up a new terminal session** for DevOps work
3. **Start with Phase 1** - Get containers running locally
4. **Iterate and improve** based on learnings

---

## 🆘 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Playwright fails in container | Install chromium deps: `playwright install-deps` |
| PostgreSQL connection fails | Check network settings, use service names not localhost |
| Jenkins can't access Docker | Mount `/var/run/docker.sock` |
| Portainer API auth fails | Generate and use API key, not username/password |
| Container restarts constantly | Check logs: `docker logs <container>` |

---

## 📚 Additional Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Jenkins Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Portainer API Docs](https://docs.portainer.io/api/docs)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Helm Chart Guide](https://helm.sh/docs/chart_template_guide/)

---

**Last Updated:** 2024-12-28
**Author:** DevOps Team
**Status:** Planning Phase
