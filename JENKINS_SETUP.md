# Jenkins CI/CD Setup Guide

Complete guide to setting up Jenkins for automated builds and deployments of Spider Price Tracker.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Initial Configuration](#initial-configuration)
4. [Pipeline Setup](#pipeline-setup)
5. [Docker Hub Integration](#docker-hub-integration)
6. [Portainer Integration](#portainer-integration)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required
- ✅ Docker and Docker Compose installed
- ✅ Docker Hub account (for image registry)
- ✅ Git repository for the project
- ✅ NAS with Portainer installed (for production deployment)

### Optional
- GitHub/GitLab account for webhook integration
- Slack/Email for notifications

---

## Quick Start

### Step 1: Start Jenkins

```bash
# Start Jenkins container
docker-compose -f docker-compose.jenkins.yml up -d

# Check logs
docker-compose -f docker-compose.jenkins.yml logs -f jenkins
```

### Step 2: Access Jenkins

1. Open browser: http://localhost:8080
2. Get initial admin password:

```bash
docker exec spider-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

3. Copy the password and paste it into Jenkins

### Step 3: Complete Setup Wizard

1. **Install Suggested Plugins** (recommended)
   - Git plugin
   - Docker plugin
   - Pipeline plugin
   - Blue Ocean (optional, modern UI)

2. **Create Admin User**
   - Username: `admin`
   - Password: `<your-secure-password>`
   - Full Name: `Spider Admin`
   - Email: `your-email@example.com`

3. **Configure Jenkins URL**
   - Use: `http://localhost:8080` (for local)
   - Or: `http://your-nas-ip:8080` (if running on NAS)

---

## Initial Configuration

### Configure Docker Access

Jenkins needs access to Docker to build images.

**Verify Docker access:**

```bash
docker exec spider-jenkins docker --version
```

If this fails, you may need to adjust permissions:

```bash
# On your host machine
sudo chmod 666 /var/run/docker.sock

# Or add Jenkins user to docker group (Linux)
docker exec -u root spider-jenkins usermod -aG docker jenkins
docker restart spider-jenkins
```

### Install Additional Plugins

1. Go to **Manage Jenkins** → **Manage Plugins**
2. Click **Available** tab
3. Search and install:
   - **Docker Pipeline**: For Docker commands in pipeline
   - **Git Parameter**: For parameterized builds
   - **Slack Notification**: For notifications (optional)
   - **Blue Ocean**: Modern UI (optional)

---

## Pipeline Setup

### Step 1: Create New Pipeline Job

1. Click **New Item**
2. Enter name: `spider-price-tracker-pipeline`
3. Select **Pipeline**
4. Click **OK**

### Step 2: Configure Pipeline

1. **General Settings**
   - ☑️ GitHub project: `https://github.com/yourusername/spider`
   - ☑️ Discard old builds: Keep 10 builds

2. **Build Triggers**
   - ☑️ GitHub hook trigger (if using GitHub)
   - ☑️ Poll SCM: `H/5 * * * *` (every 5 minutes)

3. **Pipeline Configuration**
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/yourusername/spider.git`
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`

4. Click **Save**

### Step 3: Configure Credentials

Navigate to **Manage Jenkins** → **Manage Credentials** → **(global)** → **Add Credentials**

#### Docker Hub Credentials

- Kind: **Username with password**
- Scope: **Global**
- Username: `your-dockerhub-username`
- Password: `your-dockerhub-password`
- ID: `docker-hub-credentials`
- Description: `Docker Hub Registry`

#### Database Password

- Kind: **Secret text**
- Scope: **Global**
- Secret: `your-secure-db-password`
- ID: `db-password`
- Description: `PostgreSQL Database Password`

#### Portainer URL

- Kind: **Secret text**
- Scope: **Global**
- Secret: `http://your-nas-ip:9000`
- ID: `portainer-url`
- Description: `Portainer URL`

#### Portainer API Key

1. Get API key from Portainer:
   - Login to Portainer
   - Go to **User** → **My account**
   - Click **+ Add access token**
   - Copy the token

2. Add to Jenkins:
   - Kind: **Secret text**
   - Scope: **Global**
   - Secret: `<paste-portainer-token>`
   - ID: `portainer-api-key`
   - Description: `Portainer API Key`

---

## Docker Hub Integration

### Step 1: Create Docker Hub Repository

1. Login to https://hub.docker.com
2. Click **Create Repository**
3. Name: `spider-flask`
4. Visibility: **Public** or **Private**
5. Click **Create**

6. Repeat for `spider-scraper`

### Step 2: Update Jenkinsfile (if needed)

The Jenkinsfile already uses environment variables for Docker Hub:

```groovy
environment {
    DOCKER_USERNAME = "${env.DOCKER_CREDENTIALS_USR}"
    FLASK_IMAGE = "${DOCKER_USERNAME}/spider-flask"
    SCRAPER_IMAGE = "${DOCKER_USERNAME}/spider-scraper"
}
```

---

## Portainer Integration

### Option 1: Manual Deployment

After Jenkins builds and pushes images:

1. Login to Portainer
2. Go to **Stacks** → **Add stack**
3. Name: `spider-price-tracker`
4. Web editor: Paste `docker-compose.prod.yml`
5. Add environment variables:
   - `DB_PASSWORD`
   - `DOCKER_USERNAME`
   - `WEBSITE_USERNAME`
   - `WEBSITE_PASSWORD`
6. Click **Deploy the stack**

### Option 2: Automated Deployment (Advanced)

Use the `deploy-to-portainer.sh` script:

```bash
# Set environment variables
export PORTAINER_URL="http://your-nas-ip:9000"
export PORTAINER_API_KEY="your-api-key"

# Run deployment script
./scripts/deploy-to-portainer.sh latest
```

To integrate with Jenkins, uncomment the deployment stage in Jenkinsfile:

```groovy
stage('Deploy to Production') {
    steps {
        sh './scripts/deploy-to-portainer.sh ${BUILD_VERSION}'
    }
}
```

---

## Testing the Pipeline

### Step 1: Trigger First Build

1. Go to your pipeline job
2. Click **Build Now**
3. Click on the build number (e.g., #1)
4. Click **Console Output** to watch progress

### Step 2: Verify Build Stages

The pipeline should execute:
1. ✅ Checkout code from Git
2. ✅ Build Flask image
3. ✅ Build Scraper image
4. ✅ Run tests
5. ✅ Security scan (if Trivy installed)
6. ✅ Push to Docker Hub
7. ✅ Deploy to Portainer (if configured)

### Step 3: Check Docker Hub

Verify images were pushed:

```bash
# Check Docker Hub
https://hub.docker.com/r/yourusername/spider-flask
https://hub.docker.com/r/yourusername/spider-scraper
```

---

## Webhook Setup (Optional)

### GitHub Webhook

1. Go to GitHub repo → **Settings** → **Webhooks**
2. Click **Add webhook**
3. Payload URL: `http://your-jenkins-url:8080/github-webhook/`
4. Content type: `application/json`
5. Events: **Just the push event**
6. Click **Add webhook**

Now every push to main branch triggers a build!

---

## Environment-Specific Configurations

### Development

```bash
# Use dev compose file
docker-compose -f docker-compose.dev.yml up
```

### Production (via Jenkins)

```bash
# Jenkins builds and deploys automatically
# Images pulled from Docker Hub
# Deployed to Portainer on NAS
```

---

## Monitoring and Logs

### Jenkins Logs

```bash
# Follow Jenkins logs
docker-compose -f docker-compose.jenkins.yml logs -f

# Check specific build
# Go to Jenkins UI → Job → Build #X → Console Output
```

### Application Logs (after deployment)

```bash
# On NAS via Portainer
# Stacks → spider-price-tracker → Containers → Logs

# Or via Docker CLI
docker logs spider-flask-prod
docker logs spider-scraper-prod
docker logs spider-db-prod
```

---

## Backup and Restore

### Backup Jenkins Configuration

```bash
# Backup Jenkins home directory
docker run --rm \
    -v spider_jenkins_home:/source \
    -v $(pwd)/backups:/backup \
    alpine tar czf /backup/jenkins-backup-$(date +%Y%m%d).tar.gz -C /source .
```

### Restore Jenkins Configuration

```bash
# Restore from backup
docker run --rm \
    -v spider_jenkins_home:/target \
    -v $(pwd)/backups:/backup \
    alpine tar xzf /backup/jenkins-backup-YYYYMMDD.tar.gz -C /target
```

---

## Troubleshooting

### Problem: Docker permission denied

**Solution:**
```bash
# Fix Docker socket permissions
sudo chmod 666 /var/run/docker.sock

# Or restart Jenkins
docker restart spider-jenkins
```

### Problem: Cannot push to Docker Hub

**Solution:**
```bash
# Verify credentials in Jenkins
# Manage Jenkins → Manage Credentials → Check docker-hub-credentials

# Test login manually
docker exec spider-jenkins docker login -u USERNAME -p PASSWORD
```

### Problem: Pipeline stuck at networkidle

**Solution:**
Already fixed in scraper.py with timeout handling and retry logic.

### Problem: Portainer deployment fails

**Solution:**
```bash
# Verify API key is valid
curl -H "X-API-Key: YOUR_KEY" http://your-nas-ip:9000/api/endpoints

# Check docker-compose.prod.yml syntax
docker-compose -f docker-compose.prod.yml config
```

---

## Security Best Practices

### 1. Secure Jenkins

- ✅ Enable HTTPS (use reverse proxy like Nginx)
- ✅ Strong admin password
- ✅ Enable CSRF protection
- ✅ Limit concurrent builds
- ✅ Regular backups

### 2. Secrets Management

- ✅ Use Jenkins credentials (never hardcode)
- ✅ Rotate API keys regularly
- ✅ Use `.env` files (never commit)
- ✅ Enable audit logging

### 3. Docker Images

- ✅ Scan for vulnerabilities (Trivy)
- ✅ Use specific version tags
- ✅ Minimal base images
- ✅ Non-root users

---

## Next Steps

1. ✅ **Test locally**: Build and run pipeline
2. ✅ **Configure webhooks**: Auto-build on push
3. ✅ **Set up notifications**: Slack/Email alerts
4. ✅ **Monitor**: Set up Prometheus + Grafana (Phase 4)
5. ✅ **Scale**: Add more Jenkins agents for parallel builds

---

## Resources

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Docker Pipeline Plugin](https://plugins.jenkins.io/docker-workflow/)
- [Portainer API Docs](https://docs.portainer.io/api/docs)
- [Blue Ocean Plugin](https://www.jenkins.io/projects/blueocean/)

---

**Need help?** Check the Jenkins logs or open an issue in your Git repository.
