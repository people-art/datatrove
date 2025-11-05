#!/bin/bash

# FineData Docker Services Test Script
# This script tests if all Docker services are configured correctly

set -e

echo "🧪 Testing FineData Docker Configuration..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if docker and docker-compose are installed
echo "📋 Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker is required but not installed${NC}" >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}❌ Docker Compose is required but not installed${NC}" >&2; exit 1; }
echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Validate docker-compose configuration
echo ""
echo "🔧 Validating Docker Compose configuration..."
if docker-compose config >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker Compose configuration is valid${NC}"
else
    echo -e "${RED}❌ Docker Compose configuration is invalid${NC}"
    exit 1
fi

# Check if required files exist
echo ""
echo "📁 Checking required files..."
files=("docker-compose.yml" "web/Dockerfile" "api/Dockerfile" "env.example")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file exists${NC}"
    else
        echo -e "${RED}❌ $file missing${NC}"
        exit 1
    fi
done

# Test building individual services
echo ""
echo "🏗️  Testing service builds..."

echo "Building API service..."
if docker-compose build api >/dev/null 2>&1; then
    echo -e "${GREEN}✅ API service builds successfully${NC}"
else
    echo -e "${RED}❌ API service build failed${NC}"
    exit 1
fi

echo "Building Web service..."
if docker-compose build web >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Web service builds successfully${NC}"
else
    echo -e "${RED}❌ Web service build failed${NC}"
    exit 1
fi

# Check service startup commands
echo ""
echo "🚀 Checking service startup commands..."

# Check API startup command
api_command=$(docker-compose config 2>/dev/null | grep -A 20 "api:" | grep -A 5 "command:" | grep "uvicorn" | head -1)
if [ -n "$api_command" ]; then
    echo -e "${GREEN}✅ API uses uvicorn startup command${NC}"
else
    echo -e "${RED}❌ API does not use uvicorn startup command${NC}"
    echo "Expected: uvicorn command not found in API service config"
    exit 1
fi

# Check Web startup command
web_command=$(docker-compose config 2>/dev/null | grep -A 20 "web:" | grep -A 5 "command:" | grep "npm" | head -1)
if [ -n "$web_command" ]; then
    echo -e "${GREEN}✅ Web uses npm startup command${NC}"
else
    echo -e "${RED}❌ Web does not use npm startup command${NC}"
    echo "Expected: npm command not found in Web service config"
    exit 1
fi

# Environment variables check
echo ""
echo "⚙️  Checking environment variables..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"

    # Check for required variables
    required_vars=("STRIPE_SECRET_KEY" "STRIPE_WEBHOOK_SECRET" "STRIPE_PUBLISHABLE_KEY")
    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" .env && ! grep -q "^${var}=.*your_.*_here" .env; then
            echo -e "${GREEN}✅ $var is configured${NC}"
        else
            echo -e "${YELLOW}⚠️  $var needs to be configured (currently using placeholder)${NC}"
        fi
    done
else
    echo -e "${YELLOW}⚠️  .env file not found. Copy from env.example and configure${NC}"
fi

# Port availability check
echo ""
echo "🔌 Checking port availability..."
ports=(3000 8000 5432 6379)
for port in "${ports[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $port is already in use${NC}"
    else
        echo -e "${GREEN}✅ Port $port is available${NC}"
    fi
done

# Summary
echo ""
echo "📊 Test Summary:"
echo "=================="
echo ""
echo -e "${GREEN}✅ Docker and Docker Compose are installed${NC}"
echo -e "${GREEN}✅ Docker Compose configuration is valid${NC}"
echo -e "${GREEN}✅ All required files exist${NC}"
echo -e "${GREEN}✅ API and Web services build successfully${NC}"
echo -e "${GREEN}✅ API uses uvicorn, Web uses npm for startup${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Configure your .env file with real API keys"
echo "2. Run './docker-start.sh' to start the services"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo -e "${GREEN}🎉 Docker configuration test completed successfully!${NC}"
