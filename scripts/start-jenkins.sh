#!/bin/bash

##############################################################################
# Start Jenkins CI/CD Server
#
# This script starts the Jenkins Docker container and provides
# the initial admin password for first-time setup.
##############################################################################

set -e

echo "🚀 Starting Jenkins CI/CD Server..."
echo ""

# Start Jenkins
docker compose -f docker-compose.jenkins.yml up -d

echo "⏳ Waiting for Jenkins to start (this may take 30-60 seconds)..."
sleep 30

# Wait for Jenkins to be ready
echo "⏳ Checking Jenkins health..."
for i in {1..12}; do
    if curl -s -f http://localhost:8080/login > /dev/null 2>&1; then
        echo "✅ Jenkins is ready!"
        break
    fi
    echo "   Still starting... ($i/12)"
    sleep 5
done

echo ""
echo "═══════════════════════════════════════════"
echo "✅ Jenkins Started Successfully!"
echo "═══════════════════════════════════════════"
echo ""
echo "🌐 Access Jenkins at: http://localhost:8080"
echo ""

# Get initial admin password
if docker exec spider-jenkins test -f /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null; then
    echo "🔑 Initial Admin Password:"
    echo ""
    docker exec spider-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
    echo ""
    echo ""
    echo "📋 Copy the password above and paste it into Jenkins"
else
    echo "ℹ️  Jenkins has already been configured"
    echo "   Use your admin credentials to login"
fi

echo ""
echo "📚 Next steps:"
echo "   1. Open http://localhost:8080 in your browser"
echo "   2. Follow the setup wizard"
echo "   3. Read JENKINS_SETUP.md for detailed configuration"
echo ""
echo "🔍 To view logs:"
echo "   docker compose -f docker-compose.jenkins.yml logs -f"
echo ""
echo "🛑 To stop Jenkins:"
echo "   docker compose -f docker-compose.jenkins.yml down"
echo ""
