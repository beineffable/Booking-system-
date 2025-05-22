#!/bin/bash

# Deployment script for Training Club Fitness Platform
# This script provides one-command deployment for the entire application stack

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display script usage
function show_usage {
    echo -e "${YELLOW}Usage:${NC} $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start       - Start all services"
    echo "  stop        - Stop all services"
    echo "  restart     - Restart all services"
    echo "  build       - Build or rebuild services"
    echo "  logs        - View logs from all services"
    echo "  status      - Check status of all services"
    echo "  update      - Update all services (pull latest code and rebuild)"
    echo "  backup      - Backup database"
    echo "  restore     - Restore database from backup"
    echo "  init        - Initialize the application (first-time setup)"
    echo "  help        - Show this help message"
    echo ""
}

# Function to check if Docker is installed
function check_docker {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed.${NC}"
        echo "Please install Docker and Docker Compose before running this script."
        echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Error: Docker Compose is not installed.${NC}"
        echo "Please install Docker Compose before running this script."
        echo "Visit https://docs.docker.com/compose/install/ for installation instructions."
        exit 1
    fi
}

# Function to check if .env file exists, create if not
function check_env_file {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Creating .env file with default values...${NC}"
        cat > .env << EOF
# Environment Configuration
FLASK_ENV=production

# Database Configuration
DB_USERNAME=fitness_user
DB_PASSWORD=change_this_password
DB_NAME=fitness_platform
MYSQL_ROOT_PASSWORD=change_this_root_password

# Security
JWT_SECRET_KEY=$(openssl rand -hex 32)

# API Keys (replace with your actual keys)
STRIPE_API_KEY=
TWINT_MERCHANT_ID=
MANUS_API_KEY=

# Frontend Configuration
REACT_APP_API_URL=/api
REACT_APP_STRIPE_PUBLIC_KEY=
EOF
        echo -e "${GREEN}Created .env file. Please edit it with your actual values.${NC}"
        echo -e "${YELLOW}Important: Update the passwords and API keys in the .env file before proceeding!${NC}"
        exit 1
    fi
}

# Function to create necessary directories
function create_directories {
    echo -e "${YELLOW}Creating necessary directories...${NC}"
    
    # Create nginx directories
    mkdir -p nginx/conf
    mkdir -p nginx/ssl
    mkdir -p nginx/www
    
    # Create database init directory
    mkdir -p db/init
    
    # Create backup directory
    mkdir -p backups
    
    echo -e "${GREEN}Directories created successfully.${NC}"
}

# Function to create nginx configuration
function create_nginx_config {
    echo -e "${YELLOW}Creating Nginx configuration...${NC}"
    
    cat > nginx/conf/default.conf << EOF
# Default server configuration
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
    
    echo -e "${GREEN}Nginx configuration created successfully.${NC}"
}

# Function to initialize the application
function initialize {
    echo -e "${YELLOW}Initializing the application...${NC}"
    
    # Check prerequisites
    check_docker
    check_env_file
    
    # Create necessary directories and configurations
    create_directories
    create_nginx_config
    
    # Build and start the services
    echo -e "${YELLOW}Building and starting services...${NC}"
    docker-compose up -d --build
    
    echo -e "${GREEN}Initialization complete!${NC}"
    echo -e "You can access the application at: ${YELLOW}http://localhost${NC}"
}

# Function to start all services
function start_services {
    echo -e "${YELLOW}Starting all services...${NC}"
    check_docker
    check_env_file
    docker-compose up -d
    echo -e "${GREEN}Services started successfully.${NC}"
    echo -e "You can access the application at: ${YELLOW}http://localhost${NC}"
}

# Function to stop all services
function stop_services {
    echo -e "${YELLOW}Stopping all services...${NC}"
    check_docker
    docker-compose down
    echo -e "${GREEN}Services stopped successfully.${NC}"
}

# Function to restart all services
function restart_services {
    echo -e "${YELLOW}Restarting all services...${NC}"
    check_docker
    docker-compose restart
    echo -e "${GREEN}Services restarted successfully.${NC}"
}

# Function to build or rebuild services
function build_services {
    echo -e "${YELLOW}Building all services...${NC}"
    check_docker
    check_env_file
    docker-compose build
    echo -e "${GREEN}Services built successfully.${NC}"
}

# Function to view logs from all services
function view_logs {
    echo -e "${YELLOW}Viewing logs from all services...${NC}"
    check_docker
    docker-compose logs -f
}

# Function to check status of all services
function check_status {
    echo -e "${YELLOW}Checking status of all services...${NC}"
    check_docker
    docker-compose ps
}

# Function to update all services
function update_services {
    echo -e "${YELLOW}Updating all services...${NC}"
    check_docker
    check_env_file
    
    # Pull latest code (if using git)
    if [ -d ".git" ]; then
        echo -e "${YELLOW}Pulling latest code...${NC}"
        git pull
    fi
    
    # Rebuild and restart services
    docker-compose down
    docker-compose build
    docker-compose up -d
    
    echo -e "${GREEN}Services updated successfully.${NC}"
}

# Function to backup database
function backup_database {
    echo -e "${YELLOW}Backing up database...${NC}"
    check_docker
    
    # Create timestamp for backup filename
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_FILE="backups/db_backup_${TIMESTAMP}.sql"
    
    # Create backups directory if it doesn't exist
    mkdir -p backups
    
    # Get database credentials from .env file
    source .env
    
    # Perform backup
    echo -e "${YELLOW}Creating backup file: ${BACKUP_FILE}${NC}"
    docker-compose exec -T db mysqldump -u root -p"${MYSQL_ROOT_PASSWORD}" "${DB_NAME}" > "${BACKUP_FILE}"
    
    # Check if backup was successful
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Database backup created successfully: ${BACKUP_FILE}${NC}"
    else
        echo -e "${RED}Database backup failed.${NC}"
        exit 1
    fi
}

# Function to restore database from backup
function restore_database {
    echo -e "${YELLOW}Restoring database from backup...${NC}"
    check_docker
    
    # List available backups
    echo -e "${YELLOW}Available backups:${NC}"
    ls -1 backups/*.sql 2>/dev/null
    
    # Prompt for backup file
    echo ""
    read -p "Enter backup filename to restore (or press Enter to cancel): " BACKUP_FILE
    
    if [ -z "${BACKUP_FILE}" ]; then
        echo -e "${YELLOW}Restore cancelled.${NC}"
        return
    fi
    
    if [ ! -f "${BACKUP_FILE}" ]; then
        echo -e "${RED}Error: Backup file not found.${NC}"
        exit 1
    fi
    
    # Get database credentials from .env file
    source .env
    
    # Perform restore
    echo -e "${YELLOW}Restoring from backup file: ${BACKUP_FILE}${NC}"
    docker-compose exec -T db mysql -u root -p"${MYSQL_ROOT_PASSWORD}" "${DB_NAME}" < "${BACKUP_FILE}"
    
    # Check if restore was successful
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Database restored successfully from: ${BACKUP_FILE}${NC}"
    else
        echo -e "${RED}Database restore failed.${NC}"
        exit 1
    fi
}

# Main script execution
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    build)
        build_services
        ;;
    logs)
        view_logs
        ;;
    status)
        check_status
        ;;
    update)
        update_services
        ;;
    backup)
        backup_database
        ;;
    restore)
        restore_database
        ;;
    init)
        initialize
        ;;
    help)
        show_usage
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$1'${NC}"
        show_usage
        exit 1
        ;;
esac

exit 0
