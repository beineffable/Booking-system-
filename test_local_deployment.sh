#!/bin/bash

# Test script for local deployment with Docker Compose
# This script tests the deployment of the Training Club Fitness Platform

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting local deployment test...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed.${NC}"
    exit 1
fi

# Create test .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating test .env file...${NC}"
    cp .env.example .env
    
    # Generate random passwords and keys for testing
    sed -i "s/change_this_password/testpassword123/g" .env
    sed -i "s/change_this_root_password/testrootpassword123/g" .env
    sed -i "s/change_this_to_a_random_string/$(openssl rand -hex 32)/g" .env
    sed -i "s/change_this_redis_password/testredispassword123/g" .env
fi

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p nginx/conf
mkdir -p nginx/ssl
mkdir -p nginx/www
mkdir -p db/init
mkdir -p backups

# Create nginx test configuration if it doesn't exist
if [ ! -f nginx/conf/default.conf ]; then
    echo -e "${YELLOW}Creating nginx test configuration...${NC}"
    cat > nginx/conf/default.conf << EOF
server {
    listen 80;
    listen [::]:80;
    server_name _;

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
    }

    # API requests
    location /api {
        proxy_pass http://backend:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Frontend requests
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
fi

# Stop any running containers
echo -e "${YELLOW}Stopping any running containers...${NC}"
docker-compose down

# Build the containers
echo -e "${YELLOW}Building containers...${NC}"
docker-compose build

# Check build status
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Container build failed.${NC}"
    exit 1
fi

echo -e "${GREEN}Container build successful.${NC}"

# Start the containers
echo -e "${YELLOW}Starting containers...${NC}"
docker-compose up -d

# Check if containers are running
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to start containers.${NC}"
    exit 1
fi

echo -e "${GREEN}Containers started successfully.${NC}"

# Wait for containers to initialize
echo -e "${YELLOW}Waiting for containers to initialize (30 seconds)...${NC}"
sleep 30

# Check container health
echo -e "${YELLOW}Checking container health...${NC}"
CONTAINERS=$(docker-compose ps -q)
ALL_HEALTHY=true

for CONTAINER in $CONTAINERS; do
    HEALTH=$(docker inspect --format='{{.State.Health.Status}}' $CONTAINER 2>/dev/null)
    
    # If container doesn't have health check, consider it healthy
    if [ $? -ne 0 ] || [ -z "$HEALTH" ]; then
        HEALTH="N/A"
    fi
    
    CONTAINER_NAME=$(docker inspect --format='{{.Name}}' $CONTAINER | cut -c 2-)
    
    if [ "$HEALTH" = "healthy" ] || [ "$HEALTH" = "N/A" ]; then
        echo -e "${GREEN}Container $CONTAINER_NAME is healthy or doesn't have health check.${NC}"
    else
        echo -e "${RED}Container $CONTAINER_NAME is not healthy. Status: $HEALTH${NC}"
        ALL_HEALTHY=false
    fi
done

if [ "$ALL_HEALTHY" = false ]; then
    echo -e "${RED}Error: Not all containers are healthy.${NC}"
    echo -e "${YELLOW}Checking container logs...${NC}"
    docker-compose logs
    exit 1
fi

# Test nginx proxy
echo -e "${YELLOW}Testing nginx proxy...${NC}"
curl -s http://localhost/health > /dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Nginx proxy test failed.${NC}"
    exit 1
fi

echo -e "${GREEN}Nginx proxy test successful.${NC}"

# Test backend API
echo -e "${YELLOW}Testing backend API...${NC}"
curl -s http://localhost/api/health > /dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Backend API test failed.${NC}"
    exit 1
fi

echo -e "${GREEN}Backend API test successful.${NC}"

# Test frontend
echo -e "${YELLOW}Testing frontend...${NC}"
curl -s http://localhost/ | grep -q "<title>"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Frontend test failed.${NC}"
    exit 1
fi

echo -e "${GREEN}Frontend test successful.${NC}"

# All tests passed
echo -e "${GREEN}All tests passed! Local deployment is working correctly.${NC}"
echo -e "${YELLOW}You can access the application at: http://localhost${NC}"

# Provide options to continue or stop
echo ""
echo -e "${YELLOW}Options:${NC}"
echo "1. Keep containers running"
echo "2. Stop containers"
read -p "Enter your choice (1/2): " CHOICE

if [ "$CHOICE" = "2" ]; then
    echo -e "${YELLOW}Stopping containers...${NC}"
    docker-compose down
    echo -e "${GREEN}Containers stopped.${NC}"
fi

exit 0
