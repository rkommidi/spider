# Claude DevOps Session - Starter Prompt

## Copy and paste this prompt into a new Claude terminal session:

---

```
I need you to act as a senior DevOps/SRE engineer to help me containerize and set up CI/CD for my Python Flask application.

PROJECT CONTEXT:
- Application: Spider Price Tracker (web scraper + Flask web interface)
- Current state: Monolithic app running locally with SQLite
- Location: /Users/Raghav/Work/Projects/spider
- Goal: Containerize services, migrate to PostgreSQL, set up Jenkins CI/CD, deploy to Portainer on NAS

WHAT'S ALREADY DONE:
A comprehensive DevOps transformation plan has been created with:
- Complete 4-phase strategic plan (DEVOPS_PLAN.md)
- Starter Dockerfiles for Flask and Scraper services
- docker-compose.dev.yml for local development
- Environment configuration templates
- Detailed documentation and guides

YOUR ROLE:
Act as a senior DevOps/SRE engineer helping me implement this plan. Focus on:
- Docker containerization best practices
- CI/CD pipeline implementation
- Infrastructure as Code
- Security and monitoring
- Production deployment strategies

FIRST STEPS:
1. Read the comprehensive plan: cat DEVOPS_PLAN.md
2. Review starter files: ls -la docker/
3. Understand current architecture: cat CLAUDE.md
4. Help me execute Phase 1: Local containerization

AVAILABLE DOCUMENTATION:
- DEVOPS_PLAN.md - Complete 4-phase strategic plan
- DEVOPS_README.md - Project overview and quick reference
- QUICK_START_DEVOPS.md - Practical getting started guide
- DEVOPS_SUMMARY.md - Quick summary
- docker-compose.dev.yml - Dev environment configuration
- docker/flask/Dockerfile - Flask container
- docker/scraper/Dockerfile - Scraper container

Start by reading DEVOPS_PLAN.md and then guide me through Phase 1: Containerization. Ask me questions about my environment (Docker version, NAS setup, etc.) and help me get the containers running locally first.

Let's focus on practical implementation with best practices. Be proactive in suggesting improvements to the Dockerfiles and configurations.
```

---

## Alternative Shorter Prompt (if you want to jump right in):

```
Act as a senior DevOps engineer. I'm in /Users/Raghav/Work/Projects/spider

I have a Flask price tracking app that needs:
1. Containerization (Docker)
2. PostgreSQL migration (from SQLite)
3. Jenkins CI/CD setup
4. Deployment to Portainer (on NAS)

A complete plan exists in DEVOPS_PLAN.md with starter Dockerfiles already created.

Read DEVOPS_PLAN.md first, then help me execute Phase 1: get Docker containers running locally. Ask about my environment and guide me step-by-step through containerization with best practices.
```

---

## Even Shorter "Quick Start" Prompt:

```
DevOps engineer mode: Help me containerize my Flask app in /Users/Raghav/Work/Projects/spider

Read DEVOPS_PLAN.md then guide me through Phase 1 containerization. Starter Dockerfiles exist in docker/ directory.

Goal: Get Flask + Scraper + PostgreSQL running in Docker containers locally, then later deploy to NAS with Jenkins CI/CD.

Start by reviewing the plan and asking about my environment.
```

---

## For Specific Phase Help:

### Phase 1: Containerization
```
I need help with Phase 1 of my DevOps transformation (containerization).

Project: /Users/Raghav/Work/Projects/spider
Context: Flask price tracker, migrating to Docker containers
Available: Dockerfiles in docker/, docker-compose.dev.yml, DEVOPS_PLAN.md

Help me:
1. Test the existing Dockerfiles
2. Get docker-compose working locally
3. Troubleshoot any container issues
4. Optimize for production

Read DEVOPS_PLAN.md Phase 1 section first.
```

### Phase 2: PostgreSQL Migration
```
I need help with Phase 2: migrating from SQLite to PostgreSQL.

Project: /Users/Raghav/Work/Projects/spider
Current: SQLite database with products and price history
Target: PostgreSQL in Docker container

Existing files:
- database.py (current SQLite implementation)
- docker/postgres/init.sql (starter script)
- Data in data/products.db

Help me:
1. Update database.py for PostgreSQL
2. Create migration script
3. Test data migration
4. Verify data integrity

Read DEVOPS_PLAN.md Phase 2 section.
```

### Phase 3: Jenkins CI/CD
```
I need help setting up Jenkins CI/CD pipeline.

Project: /Users/Raghav/Work/Projects/spider
Goal: Automate builds and deployments
Target: Deploy to Portainer on NAS

Setup needed:
1. Jenkins container configuration
2. Jenkinsfile pipeline
3. Docker Hub integration
4. Portainer API deployment
5. Dev and Prod environments

Read DEVOPS_PLAN.md Phase 3 section and help me configure Jenkins.
```

---

## Tips for Working with Claude in DevOps Mode:

1. **Be specific about your environment:**
   - Docker version
   - OS (macOS, Linux, Windows)
   - NAS details
   - Network setup

2. **Share error messages in full:**
   - Docker build errors
   - Container logs
   - Connection errors

3. **Ask for explanations:**
   - "Why did you choose this approach?"
   - "What are the security implications?"
   - "How does this scale?"

4. **Request best practices:**
   - "Is this the recommended way?"
   - "What would you do differently in production?"
   - "How can we make this more secure?"

5. **Iterate and improve:**
   - Share what worked/didn't work
   - Ask for optimization suggestions
   - Request code reviews

---

## Example Follow-up Questions to Ask Claude:

After the initial prompt, you can ask:

- "Review my docker-compose.dev.yml and suggest improvements"
- "What environment variables are security risks?"
- "How should I structure my Jenkins pipeline for this project?"
- "What monitoring should I add?"
- "Help me troubleshoot this Docker build error: [paste error]"
- "What's the best way to handle secrets in production?"
- "Review this Dockerfile for security issues"
- "How do I set up health checks properly?"

---

## Working Directory Commands to Run First:

When you start the new Claude session, run these first:

```bash
# Navigate to project
cd /Users/Raghav/Work/Projects/spider

# Show Claude the project structure
ls -la

# Show what documentation exists
ls -lh DEVOPS*.md QUICK_START*.md

# Show Docker files
ls -lR docker/

# Then paste your chosen prompt from above
```

---

## Recommended Workflow:

1. **Open new terminal** (or tmux)
2. **Navigate to project:** `cd /Users/Raghav/Work/Projects/spider`
3. **Start Claude Code in new session**
4. **Paste the MAIN PROMPT** (from top of this file)
5. **Let Claude read the docs** and ask you environment questions
6. **Follow Claude's guidance** step by step
7. **Share errors and logs** as they occur
8. **Iterate and improve** together

---

Good luck! 🚀
