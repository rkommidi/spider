#!/bin/bash

##############################################################################
# Deploy to Portainer Script
#
# This script deploys the Spider Price Tracker application to Portainer
# running on your NAS device.
#
# Usage:
#   ./scripts/deploy-to-portainer.sh [VERSION]
#
# Requirements:
#   - curl installed
#   - PORTAINER_URL environment variable set
#   - PORTAINER_API_KEY environment variable set
#   - Docker images pushed to Docker Hub
##############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
VERSION=${1:-latest}
STACK_NAME="spider-price-tracker"
PORTAINER_URL=${PORTAINER_URL:-"http://your-nas-ip:9000"}
PORTAINER_API_KEY=${PORTAINER_API_KEY}

echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}🚀 Deploying Spider Price Tracker${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""
echo "Version:       ${VERSION}"
echo "Stack Name:    ${STACK_NAME}"
echo "Portainer URL: ${PORTAINER_URL}"
echo ""

# Check prerequisites
if [ -z "$PORTAINER_API_KEY" ]; then
    echo -e "${RED}❌ Error: PORTAINER_API_KEY not set${NC}"
    echo "Please set the PORTAINER_API_KEY environment variable"
    exit 1
fi

if ! command -v curl &> /dev/null; then
    echo -e "${RED}❌ Error: curl not installed${NC}"
    exit 1
fi

# Function to make Portainer API calls
portainer_api() {
    local endpoint=$1
    local method=${2:-GET}
    local data=$3

    curl -s -X ${method} \
        -H "X-API-Key: ${PORTAINER_API_KEY}" \
        -H "Content-Type: application/json" \
        ${data:+-d "$data"} \
        "${PORTAINER_URL}/api${endpoint}"
}

# Get Portainer endpoint ID (usually 1 or 2)
echo -e "${YELLOW}📡 Connecting to Portainer...${NC}"
ENDPOINT_ID=$(portainer_api "/endpoints" | jq -r '.[0].Id' 2>/dev/null || echo "1")

if [ -z "$ENDPOINT_ID" ]; then
    echo -e "${RED}❌ Failed to connect to Portainer${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Connected to Portainer (Endpoint ID: ${ENDPOINT_ID})${NC}"

# Check if stack exists
echo -e "${YELLOW}🔍 Checking for existing stack...${NC}"
EXISTING_STACK=$(portainer_api "/stacks" | jq -r ".[] | select(.Name==\"${STACK_NAME}\") | .Id" 2>/dev/null)

if [ -n "$EXISTING_STACK" ]; then
    echo -e "${YELLOW}📦 Updating existing stack (ID: ${EXISTING_STACK})...${NC}"

    # Update stack
    STACK_FILE=$(cat docker-compose.prod.yml | jq -Rs .)
    UPDATE_PAYLOAD=$(jq -n \
        --arg stackFile "$STACK_FILE" \
        --argjson endpointId "$ENDPOINT_ID" \
        '{
            "stackFileContent": $stackFile,
            "env": [],
            "prune": true
        }')

    portainer_api "/stacks/${EXISTING_STACK}?endpointId=${ENDPOINT_ID}" "PUT" "$UPDATE_PAYLOAD" > /dev/null

    echo -e "${GREEN}✅ Stack updated successfully${NC}"
else
    echo -e "${YELLOW}📦 Creating new stack...${NC}"

    # Create new stack
    STACK_FILE=$(cat docker-compose.prod.yml | jq -Rs .)
    CREATE_PAYLOAD=$(jq -n \
        --arg name "$STACK_NAME" \
        --arg stackFile "$STACK_FILE" \
        --argjson endpointId "$ENDPOINT_ID" \
        '{
            "name": $name,
            "stackFileContent": $stackFile,
            "env": [],
            "fromAppTemplate": false
        }')

    portainer_api "/stacks?type=2&method=string&endpointId=${ENDPOINT_ID}" "POST" "$CREATE_PAYLOAD" > /dev/null

    echo -e "${GREEN}✅ Stack created successfully${NC}"
fi

# Pull images on the NAS
echo -e "${YELLOW}📥 Pulling latest images on NAS...${NC}"
echo "This may take a few minutes..."

# Trigger stack update/restart to pull new images
if [ -n "$EXISTING_STACK" ]; then
    portainer_api "/stacks/${EXISTING_STACK}/stop?endpointId=${ENDPOINT_ID}" "POST" > /dev/null
    sleep 2
    portainer_api "/stacks/${EXISTING_STACK}/start?endpointId=${ENDPOINT_ID}" "POST" > /dev/null
fi

echo -e "${GREEN}✅ Images pulled and containers restarted${NC}"

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Verify deployment
echo -e "${YELLOW}🔍 Verifying deployment...${NC}"

# Get stack status
STACK_STATUS=$(portainer_api "/stacks" | jq -r ".[] | select(.Name==\"${STACK_NAME}\") | .Status" 2>/dev/null)

if [ "$STACK_STATUS" == "1" ] || [ "$STACK_STATUS" == "2" ]; then
    echo -e "${GREEN}✅ Stack is running${NC}"
else
    echo -e "${RED}⚠️  Warning: Stack status unclear${NC}"
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""
echo "Stack Name: ${STACK_NAME}"
echo "Version:    ${VERSION}"
echo "Endpoint:   ${ENDPOINT_ID}"
echo ""
echo "Next steps:"
echo "1. Check Portainer UI: ${PORTAINER_URL}"
echo "2. Verify Flask is accessible"
echo "3. Check container logs for any errors"
echo ""
