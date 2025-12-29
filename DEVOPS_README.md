# DevOps Setup - Spider Price Tracker

## 📚 Documentation Index

This directory contains a complete DevOps transformation plan for the Spider Price Tracker application. Here's what each document covers:

### 1. [DEVOPS_PLAN.md](./DEVOPS_PLAN.md) - **Main Strategic Plan**
**Read this first!** Comprehensive 4-phase plan covering:
- Phase 1: Containerization (Week 1)
- Phase 2: Database Migration to PostgreSQL (Week 1-2)
- Phase 3: CI/CD with Jenkins (Week 2-3)
- Phase 4: Environment Management (Week 3)
- Architecture diagrams
- Security considerations
- Monitoring strategy

### 2. [QUICK_START_DEVOPS.md](./QUICK_START_DEVOPS.md) - **Practical Getting Started Guide**
**Your action plan!** Includes:
- How to set up your workspace
- First tasks to complete
- Essential commands
- Timeline and checklist
- Troubleshooting tips

### 3. Starter Files Created
Pre-built configuration files ready to use:
- `docker/flask/Dockerfile` - Flask app container
- `docker/scraper/Dockerfile` - Scraper container
- `docker/postgres/init.sql` - Database initialization
- `docker-compose.dev.yml` - Local development setup
- `.dockerignore` - Build optimization
- `.env.example` - Environment variables template

---

## 🎯 Quick Summary of the Plan

### Current State → Future State

**Before (Now):**
```
┌─────────────────────┐
│   Monolithic App    │
│   Flask + SQLite    │
│   Running locally   │
└─────────────────────┘
```

**After (Target):**
```
┌──────────────────────────────────────────────────┐
│              GitHub Repository                    │
└────────────┬─────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────┐
│           Jenkins CI/CD Pipeline                  │
│  Build → Test → Push to Docker Hub → Deploy     │
└────────────┬─────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────┐
│         Portainer (on NAS Device)                │
│                                                   │
│  DEV Environment        PROD Environment         │
│  ┌───────────────┐     ┌───────────────┐        │
│  │ Flask :5001   │     │ Flask :5000   │        │
│  │ Scraper       │     │ Scraper       │        │
│  │ PostgreSQL    │     │ PostgreSQL    │        │
│  └───────────────┘     └───────────────┘        │
└──────────────────────────────────────────────────┘
```

### Services Breakdown

| Service | Purpose | Port | Schedule |
|---------|---------|------|----------|
| **Flask** | Web UI | 5000/5001 | Always running |
| **Scraper** | Data collection | N/A | Cron (daily) |
| **PostgreSQL** | Database | 5432/5433 | Always running |
| **Jenkins** | CI/CD | 8080 | Always running |

---

## 🚀 How to Get Started (30 Seconds)

### Option 1: Start Local Development
```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env with your credentials
vim .env  # or use your editor

# 3. Start all services
docker-compose -f docker-compose.dev.yml up -d

# 4. Check status
docker-compose -f docker-compose.dev.yml ps

# 5. View Flask app
open http://localhost:5000
```

### Option 2: Start Planning Phase
```bash
# 1. Read the strategic plan
cat DEVOPS_PLAN.md | less

# 2. Read the quick start guide
cat QUICK_START_DEVOPS.md | less

# 3. Schedule meeting with DevOps engineer
# Review both documents together
```

---

## 📋 Pre-requisites Checklist

Before you begin, ensure you have:

### Software Requirements
- [ ] **Docker** (20.10+) - `docker --version`
- [ ] **Docker Compose** (2.0+) - `docker-compose --version`
- [ ] **Git** - `git --version`
- [ ] **Text Editor** (VS Code, Vim, etc.)

### Access Requirements
- [ ] **Docker Hub account** - For hosting images
- [ ] **GitHub access** - For CI/CD integration
- [ ] **NAS access** - For Portainer deployment
- [ ] **Website credentials** - For scraper

### Knowledge Requirements (Nice to Have)
- [ ] Basic Docker understanding
- [ ] SQL basics (for migration)
- [ ] Linux command line
- [ ] Understanding of CI/CD concepts

---

## 🗂️ Project Structure After Setup

```
spider/
├── app.py                      # Flask application
├── scraper.py                  # Scraper logic
├── database.py                 # Database layer
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (git-ignored)
├── .env.example               # Template for .env
├── .dockerignore              # Docker build exclusions
│
├── docker/                     # Docker configuration
│   ├── flask/
│   │   └── Dockerfile         # Flask container definition
│   ├── scraper/
│   │   └── Dockerfile         # Scraper container definition
│   ├── postgres/
│   │   ├── Dockerfile
│   │   └── init.sql           # Database initialization
│   └── jenkins/
│       └── Dockerfile
│
├── docker-compose.dev.yml     # Dev environment
├── docker-compose.prod.yml    # Prod environment (to be created)
│
├── migrations/                 # Database migration scripts
│   └── migrate_sqlite_to_postgres.py
│
├── jenkins/                    # CI/CD configuration
│   ├── Jenkinsfile            # Pipeline definition
│   └── pipelines/
│
├── helm/                       # Kubernetes charts (optional)
│   └── spider-chart/
│       ├── Chart.yaml
│       ├── values.dev.yaml
│       └── templates/
│
├── monitoring/                 # Observability (future)
│   ├── prometheus/
│   └── grafana/
│
└── docs/                       # Documentation
    ├── DEVOPS_PLAN.md         # Strategic plan
    ├── QUICK_START_DEVOPS.md  # Getting started
    └── DEVOPS_README.md       # This file
```

---

## 🎓 Learning Path

If you're new to DevOps, follow this learning path:

### Week 1: Docker Basics
1. Complete Docker's official "Getting Started" tutorial
2. Understand Dockerfile syntax
3. Learn docker-compose basics
4. Practice building and running containers

### Week 2: Database & Networking
1. Understand Docker networks
2. Learn PostgreSQL basics
3. Practice database migrations
4. Understand volume management

### Week 3: CI/CD Concepts
1. Learn Jenkins basics
2. Understand pipeline concepts
3. Practice writing Jenkinsfile
4. Learn about container registries

### Week 4: Production Deployment
1. Understand Portainer
2. Learn about secrets management
3. Practice monitoring and logging
4. Study disaster recovery

---

## 🔄 Workflow After Setup

### Daily Development Workflow
```bash
# 1. Start dev environment
docker-compose -f docker-compose.dev.yml up -d

# 2. Make code changes (hot reload enabled)
vim app.py

# 3. View logs
docker-compose -f docker-compose.dev.yml logs -f flask

# 4. Run scraper manually
docker-compose -f docker-compose.dev.yml run scraper

# 5. Stop environment
docker-compose -f docker-compose.dev.yml down
```

### CI/CD Workflow (After Setup)
```bash
# 1. Commit and push code
git add .
git commit -m "Add new feature"
git push origin main

# 2. Jenkins automatically:
#    - Detects push via webhook
#    - Builds Docker images
#    - Runs tests
#    - Pushes to Docker Hub
#    - Deploys to dev environment

# 3. For production deployment:
#    - Create git tag: git tag v1.0.0
#    - Push tag: git push origin v1.0.0
#    - Manual approval in Jenkins
#    - Deploy to production
```

---

## 🐛 Common Issues & Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Port already in use | `docker-compose down` or change port in yml |
| Permission denied | Add user to docker group: `sudo usermod -aG docker $USER` |
| Container won't start | Check logs: `docker logs <container_name>` |
| Database connection failed | Verify DATABASE_URL in .env |
| Build is slow | Use `.dockerignore` properly |
| Out of disk space | Clean up: `docker system prune -a` |

---

## 📞 Getting Help

### During Development
1. Check logs: `docker-compose logs -f`
2. Shell into container: `docker exec -it spider-flask-dev /bin/bash`
3. Review documentation in this repo
4. Check Stack Overflow with specific error messages

### For DevOps Issues
1. Review DEVOPS_PLAN.md troubleshooting section
2. Check Docker documentation
3. Review Jenkins pipeline logs
4. Consult with your DevOps engineer

---

## 🎯 Success Metrics

After completing the setup, you should be able to:

✅ **Development**
- [ ] Start entire stack with one command
- [ ] Make code changes with hot reload
- [ ] Run scraper on demand
- [ ] Access PostgreSQL database

✅ **CI/CD**
- [ ] Automatic builds on git push
- [ ] Automated testing
- [ ] One-click deployment to dev
- [ ] Manual approval for prod

✅ **Operations**
- [ ] Monitor application health
- [ ] View centralized logs
- [ ] Backup and restore database
- [ ] Roll back deployments

---

## 📅 Milestones

- [ ] **Milestone 1:** Local containers running (Week 1)
- [ ] **Milestone 2:** PostgreSQL migration complete (Week 2)
- [ ] **Milestone 3:** Jenkins pipeline working (Week 3)
- [ ] **Milestone 4:** Dev environment on NAS (Week 3)
- [ ] **Milestone 5:** Production deployment (Week 4)
- [ ] **Milestone 6:** Monitoring enabled (Week 5)

---

## 🚀 Next Steps

1. **Right Now:**
   - Read DEVOPS_PLAN.md (15 minutes)
   - Read QUICK_START_DEVOPS.md (10 minutes)
   - Try starting local containers (5 minutes)

2. **Today:**
   - Set up .env file with credentials
   - Build and test Docker containers locally
   - Document any issues

3. **This Week:**
   - Complete Phase 1 (Containerization)
   - Test PostgreSQL migration
   - Schedule meeting with DevOps engineer

4. **This Month:**
   - Complete all 4 phases
   - Deploy to NAS
   - Monitor for 1 week before calling it "done"

---

## 📝 Feedback & Improvements

This is a living document. As you progress:
- Document lessons learned
- Update scripts with improvements
- Share knowledge with the team
- Iterate on the process

---

**Good luck with your DevOps transformation!** 🎉

*Last updated: 2024-12-28*
