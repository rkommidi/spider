# Quick Start Guide - DevOps Transformation

## 🚀 How to Start Working on DevOps Tasks

### Step 1: Open New Terminal Session
You mentioned wanting to work with a senior DevOps/SRE engineer. Here's how to organize:

**Option A: Separate Terminal Window**
```bash
# Open a new terminal window/tab and navigate to project
cd /Users/Raghav/Work/Projects/spider

# You can now work on DevOps tasks here while keeping
# the main development in your current Claude session
```

**Option B: Use tmux for Split Sessions**
```bash
# Install tmux if not already installed
brew install tmux

# Start tmux session
tmux new -s devops

# Split horizontally: Ctrl+b then "
# Split vertically: Ctrl+b then %
# Switch panes: Ctrl+b then arrow keys
```

---

## 📋 First Tasks (Do These First!)

### Task 1: Review the DevOps Plan
```bash
# Read the comprehensive plan
cat DEVOPS_PLAN.md

# Or open in your editor
code DEVOPS_PLAN.md  # VS Code
vim DEVOPS_PLAN.md   # Vim
```

### Task 2: Create Directory Structure
```bash
# Create all necessary directories
mkdir -p docker/{flask,scraper,postgres,jenkins}
mkdir -p helm/spider-chart/{templates,values}
mkdir -p jenkins/pipelines
mkdir -p migrations
mkdir -p monitoring/{prometheus,grafana}

# Verify structure
tree -L 3
```

### Task 3: Create Initial Docker Files
```bash
# We'll create these files together
touch docker/flask/Dockerfile
touch docker/scraper/Dockerfile
touch docker/postgres/Dockerfile
touch docker/postgres/init.sql
touch docker-compose.dev.yml
touch docker-compose.prod.yml
touch .dockerignore
```

### Task 4: Update Requirements
```bash
# Add production-ready dependencies
cat >> requirements.txt << EOF

# Production server
gunicorn==21.2.0

# PostgreSQL adapter
psycopg2-binary==2.9.9

# Environment management
python-dotenv==1.0.0

# Health checks
health-check==3.4.1
EOF
```

---

## 🎯 Suggested Work Division

### You (Developer) Focus On:
- ✅ Application code improvements
- ✅ Database schema migrations
- ✅ Testing application logic
- ✅ Frontend improvements

### DevOps Engineer Focus On:
- 🔧 Dockerfile optimization
- 🔧 CI/CD pipeline configuration
- 🔧 Infrastructure as Code (Helm charts)
- 🔧 Monitoring & alerting setup
- 🔧 Security hardening
- 🔧 Portainer configuration

### Collaborate On:
- 🤝 Environment variable management
- 🤝 Database migration strategy
- 🤝 Deployment rollout plans
- 🤝 Troubleshooting production issues

---

## 📅 Recommended Timeline

### Week 1: Foundation
**Days 1-2: Local Containerization**
- Create Dockerfiles
- Test containers locally
- Get docker-compose working

**Days 3-4: Database Migration**
- Set up PostgreSQL container
- Update database.py for PostgreSQL
- Test migration script

**Day 5: Documentation & Review**
- Document any issues encountered
- Review with team

### Week 2: CI/CD Setup
**Days 1-2: Jenkins Configuration**
- Set up Jenkins container
- Install necessary plugins
- Configure credentials

**Days 3-4: Pipeline Development**
- Write Jenkinsfile
- Test build pipeline
- Test deployment to dev

**Day 5: Testing & Refinement**
- End-to-end pipeline test
- Fix any issues

### Week 3: Production Deployment
**Days 1-2: Portainer Setup**
- Configure NAS device
- Set up Portainer stacks
- Test deployments

**Days 3-4: Monitoring & Hardening**
- Add health checks
- Set up basic monitoring
- Security review

**Day 5: Go-Live Planning**
- Create runbooks
- Disaster recovery plan
- Production deployment

---

## 🔧 Essential Commands Reference

### Docker Commands
```bash
# Build image
docker build -t spider-flask:latest -f docker/flask/Dockerfile .

# Run container
docker run -p 5000:5000 spider-flask:latest

# View logs
docker logs -f <container_name>

# Shell into container
docker exec -it <container_name> /bin/bash

# Clean up
docker system prune -a
```

### Docker Compose Commands
```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down

# Rebuild and restart
docker-compose -f docker-compose.dev.yml up -d --build
```

### PostgreSQL Commands
```bash
# Connect to PostgreSQL container
docker exec -it spider-db-dev psql -U spider -d spider_dev

# Backup database
docker exec spider-db-dev pg_dump -U spider spider_dev > backup.sql

# Restore database
docker exec -i spider-db-dev psql -U spider spider_dev < backup.sql
```

---

## ✅ Pre-Flight Checklist

Before starting, make sure you have:

- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] Git configured
- [ ] Access to Docker Hub account
- [ ] NAS device accessible on network
- [ ] Portainer installed on NAS
- [ ] Text editor/IDE ready
- [ ] Read the DEVOPS_PLAN.md document
- [ ] DevOps engineer has access to repo

---

## 🆘 Getting Help

### If Docker Build Fails
1. Check Dockerfile syntax
2. Review build logs: `docker build --no-cache ...`
3. Verify base image exists
4. Check network connectivity

### If Containers Won't Start
1. Check logs: `docker logs <container>`
2. Verify environment variables
3. Check port conflicts: `lsof -i :5000`
4. Verify dependencies are running

### If Database Connection Fails
1. Check PostgreSQL is running
2. Verify credentials in .env file
3. Check network (use service name, not localhost)
4. Test connection: `psql postgresql://user:pass@host:5432/db`

---

## 📞 Communication Template

When working with your DevOps engineer, use this format for clear communication:

```
## Task: [Brief description]

**Priority:** High/Medium/Low
**Blocked by:** [Any dependencies]
**Environment:** Dev/Prod/Both

**Current Status:**
- What's working
- What's not working

**Next Steps:**
1. Step one
2. Step two

**Questions:**
- Any blockers or questions
```

---

## 🎓 Learning Resources

If you're new to any of these technologies:

**Docker:**
- Official Tutorial: https://docs.docker.com/get-started/
- Best Practices: https://docs.docker.com/develop/dev-best-practices/

**Jenkins:**
- Pipeline Tutorial: https://www.jenkins.io/doc/book/pipeline/
- Docker Integration: https://www.jenkins.io/doc/book/pipeline/docker/

**PostgreSQL:**
- Docker Setup: https://hub.docker.com/_/postgres
- Migration Guide: https://wiki.postgresql.org/wiki/Converting_from_other_Databases_to_PostgreSQL

**Portainer:**
- Getting Started: https://docs.portainer.io/start/intro
- API Documentation: https://docs.portainer.io/api/docs

---

## 🚦 Ready to Start?

1. ✅ Read DEVOPS_PLAN.md
2. ✅ Create directory structure (see Task 2 above)
3. ✅ Meet with DevOps engineer to divide tasks
4. ✅ Start with Phase 1: Local Containerization

**First concrete task:** Create the Flask Dockerfile and test it locally!

Good luck! 🎉
