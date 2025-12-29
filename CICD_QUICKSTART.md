# CI/CD Quick Start Guide

Fast track to getting your Jenkins pipeline running in 10 minutes.

## ⚡ Quick Setup (5 Commands)

```bash
# 1. Start Jenkins
./scripts/start-jenkins.sh

# 2. Get admin password (will be displayed)
# Copy the password from the terminal output

# 3. Open Jenkins
open http://localhost:8080

# 4. Complete wizard (install suggested plugins)

# 5. Create pipeline job pointing to your Jenkinsfile
```

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Docker and Docker Compose installed
- [ ] Docker Hub account created
- [ ] Git repository for this project
- [ ] NAS with Portainer installed (for production)
- [ ] This project cloned locally

---

## 🚀 Step-by-Step

### 1. Start Jenkins (1 minute)

```bash
./scripts/start-jenkins.sh
```

Wait for the initial admin password to appear in the terminal.

### 2. Initial Setup (3 minutes)

1. Open: http://localhost:8080
2. Paste the admin password
3. Click **Install suggested plugins**
4. Create admin user:
   - Username: `admin`
   - Password: `<your-password>`
   - Email: `your@email.com`
5. Keep Jenkins URL as `http://localhost:8080`
6. Click **Start using Jenkins**

### 3. Add Credentials (2 minutes)

Go to **Manage Jenkins** → **Manage Credentials** → **(global)** → **Add Credentials**

Add these 4 credentials:

**a) Docker Hub** (ID: `docker-hub-credentials`)
```
Kind: Username with password
Username: your-dockerhub-username
Password: your-dockerhub-password
```

**b) DB Password** (ID: `db-password`)
```
Kind: Secret text
Secret: your-secure-db-password
```

**c) Portainer URL** (ID: `portainer-url`)
```
Kind: Secret text
Secret: http://your-nas-ip:9000
```

**d) Portainer API Key** (ID: `portainer-api-key`)
```
Kind: Secret text
Secret: <get from Portainer → My Account → Add access token>
```

### 4. Create Pipeline (2 minutes)

1. Click **New Item**
2. Name: `spider-price-tracker`
3. Type: **Pipeline**
4. Click **OK**

Configure:
- **General**: ☑️ GitHub project (if applicable)
- **Pipeline**:
  - Definition: **Pipeline script from SCM**
  - SCM: **Git**
  - Repository URL: `<your-git-repo-url>`
  - Branch: `*/main`
  - Script Path: `Jenkinsfile`
- Click **Save**

### 5. Run First Build (2 minutes)

1. Click **Build Now**
2. Click build number (e.g., #1)
3. Click **Console Output**
4. Watch the build progress!

---

## 📊 Pipeline Stages

Your build will go through these stages:

1. ✅ **Checkout** - Pull code from Git
2. ✅ **Build Images** - Build Flask & Scraper (parallel)
3. ✅ **Test** - Run database connectivity tests
4. ✅ **Security Scan** - Scan for vulnerabilities
5. ✅ **Push** - Push to Docker Hub (main branch only)
6. ✅ **Deploy** - Deploy to Portainer (main branch only)
7. ✅ **Verify** - Health check deployment

---

## 🐳 Docker Hub Setup

### Create Repositories

1. Go to https://hub.docker.com
2. Click **Create Repository**
3. Create TWO repositories:
   - `spider-flask` (Public or Private)
   - `spider-scraper` (Public or Private)

### Update Jenkinsfile (if needed)

The Jenkinsfile uses your Docker Hub username from credentials.
No changes needed!

---

## 🎯 Common Tasks

### View Jenkins Logs

```bash
docker-compose -f docker-compose.jenkins.yml logs -f
```

### Stop Jenkins

```bash
docker-compose -f docker-compose.jenkins.yml down
```

### Restart Jenkins

```bash
docker-compose -f docker-compose.jenkins.yml restart
```

### Backup Jenkins Data

```bash
docker run --rm \
  -v spider_jenkins_home:/source \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/jenkins-$(date +%Y%m%d).tar.gz -C /source .
```

### Check Jenkins Container

```bash
docker ps | grep jenkins
docker exec -it spider-jenkins bash
```

---

## 🔧 Troubleshooting

### Jenkins won't start

```bash
# Check logs
docker-compose -f docker-compose.jenkins.yml logs

# Verify Docker is running
docker ps

# Check port 8080 is available
lsof -i :8080
```

### Build fails at Docker step

```bash
# Verify Docker socket access
docker exec spider-jenkins docker ps

# Fix permissions if needed
sudo chmod 666 /var/run/docker.sock
```

### Cannot push to Docker Hub

```bash
# Verify credentials
# Go to Jenkins → Manage Credentials → Check docker-hub-credentials

# Test login manually
docker exec spider-jenkins docker login -u USERNAME -p PASSWORD
```

### Pipeline says "No such file Jenkinsfile"

Check:
1. Jenkinsfile exists in repo root
2. Git repository URL is correct
3. Branch name is correct (main vs master)

---

## 📚 Full Documentation

For detailed setup and advanced configuration:
- **Complete Guide**: Read `JENKINS_SETUP.md`
- **DevOps Plan**: Read `DEVOPS_PLAN.md`

---

## ✅ Success Checklist

After setup, verify:

- [ ] Jenkins accessible at http://localhost:8080
- [ ] Pipeline job created
- [ ] All 4 credentials configured
- [ ] First build completes successfully
- [ ] Images appear in Docker Hub
- [ ] Can access Portainer on NAS

---

## 🎉 You're Done!

Your CI/CD pipeline is now ready!

**Every time you push to main:**
1. Jenkins automatically builds
2. Images are pushed to Docker Hub
3. Application deploys to your NAS
4. You get notified of results

---

## 🔗 Useful Links

- Jenkins: http://localhost:8080
- Docker Hub: https://hub.docker.com
- Portainer: http://your-nas-ip:9000
- Flask App (prod): http://your-nas-ip:5000

---

**Questions?** Check `JENKINS_SETUP.md` for detailed troubleshooting.
