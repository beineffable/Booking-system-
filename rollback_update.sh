#!/bin/bash

# Rollback and Update Script for Training Club Fitness Platform
# This script provides functionality for safe updates and rollbacks

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
    echo "  update              - Update to the latest version"
    echo "  rollback            - Rollback to the previous version"
    echo "  rollback-to [tag]   - Rollback to a specific version tag"
    echo "  snapshot            - Create a snapshot of the current state"
    echo "  list-snapshots      - List available snapshots"
    echo "  help                - Show this help message"
    echo ""
}

# Function to check if Docker is installed
function check_docker {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed.${NC}"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Error: Docker Compose is not installed.${NC}"
        exit 1
    fi
}

# Function to check if git is installed
function check_git {
    if ! command -v git &> /dev/null; then
        echo -e "${RED}Error: Git is not installed.${NC}"
        exit 1
    fi
}

# Function to create a snapshot of the current state
function create_snapshot {
    echo -e "${YELLOW}Creating snapshot of the current state...${NC}"
    
    # Check prerequisites
    check_docker
    
    # Create snapshots directory if it doesn't exist
    mkdir -p snapshots
    
    # Create timestamp for snapshot name
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    SNAPSHOT_DIR="snapshots/snapshot_${TIMESTAMP}"
    
    # Create snapshot directory
    mkdir -p "${SNAPSHOT_DIR}"
    
    # Backup environment variables
    echo -e "${YELLOW}Backing up environment variables...${NC}"
    if [ -f .env ]; then
        cp .env "${SNAPSHOT_DIR}/env_backup"
    fi
    
    # Backup docker-compose configuration
    echo -e "${YELLOW}Backing up docker-compose configuration...${NC}"
    cp docker-compose.yml "${SNAPSHOT_DIR}/docker-compose.yml"
    
    # Backup Nginx configuration
    echo -e "${YELLOW}Backing up Nginx configuration...${NC}"
    if [ -d nginx/conf ]; then
        mkdir -p "${SNAPSHOT_DIR}/nginx/conf"
        cp -r nginx/conf/* "${SNAPSHOT_DIR}/nginx/conf/"
    fi
    
    # Backup SSL certificates
    echo -e "${YELLOW}Backing up SSL certificates...${NC}"
    if [ -d nginx/ssl ]; then
        mkdir -p "${SNAPSHOT_DIR}/nginx/ssl"
        cp -r nginx/ssl/* "${SNAPSHOT_DIR}/nginx/ssl/"
    fi
    
    # Backup database
    echo -e "${YELLOW}Backing up database...${NC}"
    if [ -f .env ]; then
        source .env
        BACKUP_FILE="${SNAPSHOT_DIR}/db_backup.sql"
        docker-compose exec -T db mysqldump -u root -p"${MYSQL_ROOT_PASSWORD}" "${DB_NAME}" > "${BACKUP_FILE}"
    fi
    
    # Save git commit hash if in a git repository
    if [ -d .git ]; then
        echo -e "${YELLOW}Saving git commit hash...${NC}"
        git rev-parse HEAD > "${SNAPSHOT_DIR}/git_commit"
    fi
    
    # Save docker image tags
    echo -e "${YELLOW}Saving docker image tags...${NC}"
    docker-compose config | grep image: > "${SNAPSHOT_DIR}/docker_images"
    
    # Create snapshot metadata
    echo -e "${YELLOW}Creating snapshot metadata...${NC}"
    cat > "${SNAPSHOT_DIR}/metadata.json" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "snapshot_id": "snapshot_${TIMESTAMP}",
    "description": "Automatic snapshot before update",
    "services": [
        $(docker-compose ps --services | sed 's/^/        "/g' | sed 's/$/",/g' | sed '$ s/,$//')
    ]
}
EOF
    
    echo -e "${GREEN}Snapshot created successfully: ${SNAPSHOT_DIR}${NC}"
    
    # Return snapshot ID
    echo "snapshot_${TIMESTAMP}"
}

# Function to list available snapshots
function list_snapshots {
    echo -e "${YELLOW}Available snapshots:${NC}"
    
    # Check if snapshots directory exists
    if [ ! -d snapshots ]; then
        echo -e "${YELLOW}No snapshots found.${NC}"
        return
    fi
    
    # List snapshots with metadata
    for snapshot in snapshots/snapshot_*; do
        if [ -d "$snapshot" ] && [ -f "${snapshot}/metadata.json" ]; then
            SNAPSHOT_ID=$(basename "$snapshot")
            TIMESTAMP=$(jq -r '.timestamp' "${snapshot}/metadata.json" 2>/dev/null)
            DESCRIPTION=$(jq -r '.description' "${snapshot}/metadata.json" 2>/dev/null)
            
            if [ -z "$TIMESTAMP" ] || [ -z "$DESCRIPTION" ]; then
                TIMESTAMP=$(date -r "$snapshot" "+%Y-%m-%d %H:%M:%S")
                DESCRIPTION="Unknown"
            fi
            
            echo -e "${GREEN}${SNAPSHOT_ID}${NC}"
            echo -e "  Created: ${TIMESTAMP}"
            echo -e "  Description: ${DESCRIPTION}"
            
            # Show git commit if available
            if [ -f "${snapshot}/git_commit" ]; then
                GIT_COMMIT=$(cat "${snapshot}/git_commit")
                echo -e "  Git commit: ${GIT_COMMIT}"
            fi
            
            echo ""
        fi
    done
}

# Function to update to the latest version
function update_platform {
    echo -e "${YELLOW}Updating platform to the latest version...${NC}"
    
    # Check prerequisites
    check_docker
    check_git
    
    # Create snapshot before update
    echo -e "${YELLOW}Creating snapshot before update...${NC}"
    SNAPSHOT_ID=$(create_snapshot)
    
    # Pull latest code
    echo -e "${YELLOW}Pulling latest code...${NC}"
    git pull
    
    # Check if pull was successful
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to pull latest code.${NC}"
        echo -e "${YELLOW}Rolling back to previous state...${NC}"
        rollback_to_snapshot "$SNAPSHOT_ID"
        exit 1
    fi
    
    # Build and restart services
    echo -e "${YELLOW}Building and restarting services...${NC}"
    docker-compose down
    docker-compose build
    docker-compose up -d
    
    # Check if services started successfully
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to start services.${NC}"
        echo -e "${YELLOW}Rolling back to previous state...${NC}"
        rollback_to_snapshot "$SNAPSHOT_ID"
        exit 1
    fi
    
    # Wait for services to initialize
    echo -e "${YELLOW}Waiting for services to initialize (30 seconds)...${NC}"
    sleep 30
    
    # Check service health
    echo -e "${YELLOW}Checking service health...${NC}"
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
        echo -e "${RED}Error: Not all services are healthy after update.${NC}"
        echo -e "${YELLOW}Rolling back to previous state...${NC}"
        rollback_to_snapshot "$SNAPSHOT_ID"
        exit 1
    fi
    
    echo -e "${GREEN}Update completed successfully!${NC}"
}

# Function to rollback to a specific snapshot
function rollback_to_snapshot {
    SNAPSHOT_ID=$1
    
    echo -e "${YELLOW}Rolling back to snapshot: ${SNAPSHOT_ID}...${NC}"
    
    # Check prerequisites
    check_docker
    
    # Check if snapshot exists
    SNAPSHOT_DIR="snapshots/${SNAPSHOT_ID}"
    if [ ! -d "$SNAPSHOT_DIR" ]; then
        echo -e "${RED}Error: Snapshot not found: ${SNAPSHOT_ID}${NC}"
        exit 1
    fi
    
    # Stop services
    echo -e "${YELLOW}Stopping services...${NC}"
    docker-compose down
    
    # Restore environment variables
    echo -e "${YELLOW}Restoring environment variables...${NC}"
    if [ -f "${SNAPSHOT_DIR}/env_backup" ]; then
        cp "${SNAPSHOT_DIR}/env_backup" .env
    fi
    
    # Restore docker-compose configuration
    echo -e "${YELLOW}Restoring docker-compose configuration...${NC}"
    cp "${SNAPSHOT_DIR}/docker-compose.yml" docker-compose.yml
    
    # Restore Nginx configuration
    echo -e "${YELLOW}Restoring Nginx configuration...${NC}"
    if [ -d "${SNAPSHOT_DIR}/nginx/conf" ]; then
        mkdir -p nginx/conf
        cp -r "${SNAPSHOT_DIR}/nginx/conf/"* nginx/conf/
    fi
    
    # Restore SSL certificates
    echo -e "${YELLOW}Restoring SSL certificates...${NC}"
    if [ -d "${SNAPSHOT_DIR}/nginx/ssl" ]; then
        mkdir -p nginx/ssl
        cp -r "${SNAPSHOT_DIR}/nginx/ssl/"* nginx/ssl/
    fi
    
    # Restore git commit if available
    if [ -f "${SNAPSHOT_DIR}/git_commit" ] && [ -d .git ]; then
        echo -e "${YELLOW}Restoring git commit...${NC}"
        GIT_COMMIT=$(cat "${SNAPSHOT_DIR}/git_commit")
        git checkout $GIT_COMMIT
    fi
    
    # Start services
    echo -e "${YELLOW}Starting services...${NC}"
    docker-compose up -d
    
    # Restore database if needed
    echo -e "${YELLOW}Checking if database restore is needed...${NC}"
    if [ -f "${SNAPSHOT_DIR}/db_backup.sql" ]; then
        echo -e "${YELLOW}Waiting for database to initialize (10 seconds)...${NC}"
        sleep 10
        
        echo -e "${YELLOW}Restoring database...${NC}"
        source .env
        docker-compose exec -T db mysql -u root -p"${MYSQL_ROOT_PASSWORD}" "${DB_NAME}" < "${SNAPSHOT_DIR}/db_backup.sql"
    fi
    
    echo -e "${GREEN}Rollback completed successfully!${NC}"
}

# Function to rollback to the previous version
function rollback_platform {
    echo -e "${YELLOW}Rolling back to the previous version...${NC}"
    
    # Check if snapshots directory exists
    if [ ! -d snapshots ]; then
        echo -e "${RED}Error: No snapshots found.${NC}"
        exit 1
    fi
    
    # Find the most recent snapshot
    LATEST_SNAPSHOT=$(ls -td snapshots/snapshot_* | head -n 1 | xargs basename)
    
    if [ -z "$LATEST_SNAPSHOT" ]; then
        echo -e "${RED}Error: No snapshots found.${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Found latest snapshot: ${LATEST_SNAPSHOT}${NC}"
    
    # Rollback to the snapshot
    rollback_to_snapshot "$LATEST_SNAPSHOT"
}

# Function to rollback to a specific version tag
function rollback_to_tag {
    TAG=$1
    
    echo -e "${YELLOW}Rolling back to version tag: ${TAG}...${NC}"
    
    # Check prerequisites
    check_docker
    check_git
    
    # Create snapshot before rollback
    echo -e "${YELLOW}Creating snapshot before rollback...${NC}"
    create_snapshot
    
    # Check if tag exists
    if ! git rev-parse "$TAG" >/dev/null 2>&1; then
        echo -e "${RED}Error: Tag not found: ${TAG}${NC}"
        exit 1
    fi
    
    # Checkout tag
    echo -e "${YELLOW}Checking out tag: ${TAG}...${NC}"
    git checkout "$TAG"
    
    # Check if checkout was successful
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to checkout tag: ${TAG}${NC}"
        exit 1
    fi
    
    # Build and restart services
    echo -e "${YELLOW}Building and restarting services...${NC}"
    docker-compose down
    docker-compose build
    docker-compose up -d
    
    echo -e "${GREEN}Rollback to tag ${TAG} completed successfully!${NC}"
}

# Main script execution
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

COMMAND=$1
TAG=$2

case "$COMMAND" in
    update)
        update_platform
        ;;
    rollback)
        rollback_platform
        ;;
    rollback-to)
        if [ -z "$TAG" ]; then
            echo -e "${RED}Error: Tag or snapshot ID is required.${NC}"
            show_usage
            exit 1
        fi
        
        # Check if it's a snapshot ID or a git tag
        if [[ "$TAG" == snapshot_* ]]; then
            rollback_to_snapshot "$TAG"
        else
            rollback_to_tag "$TAG"
        fi
        ;;
    snapshot)
        create_snapshot
        ;;
    list-snapshots)
        list_snapshots
        ;;
    help)
        show_usage
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$COMMAND'${NC}"
        show_usage
        exit 1
        ;;
esac

exit 0
