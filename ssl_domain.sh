#!/bin/bash

# SSL and Domain Configuration Script for Training Club Fitness Platform
# This script automates SSL certificate provisioning and domain configuration

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display script usage
function show_usage {
    echo -e "${YELLOW}Usage:${NC} $0 [command] [domain]"
    echo ""
    echo "Commands:"
    echo "  setup       - Set up SSL and domain configuration"
    echo "  renew       - Renew SSL certificates"
    echo "  status      - Check SSL certificate status"
    echo "  help        - Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 setup fitness.trainingclub.ch"
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

# Function to check if domain is provided
function check_domain {
    if [ -z "$DOMAIN" ]; then
        echo -e "${RED}Error: Domain name is required.${NC}"
        show_usage
        exit 1
    fi
}

# Function to check if certbot is installed
function check_certbot {
    if ! command -v certbot &> /dev/null; then
        echo -e "${YELLOW}Certbot not found. Installing...${NC}"
        apt-get update
        apt-get install -y certbot
    fi
}

# Function to set up SSL and domain configuration
function setup_ssl_domain {
    echo -e "${YELLOW}Setting up SSL and domain configuration for ${DOMAIN}...${NC}"
    
    # Check prerequisites
    check_docker
    check_domain
    check_certbot
    
    # Create directories if they don't exist
    mkdir -p nginx/ssl
    mkdir -p nginx/conf
    
    # Create initial Nginx configuration for domain validation
    echo -e "${YELLOW}Creating initial Nginx configuration for domain validation...${NC}"
    cat > nginx/conf/default.conf << EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN};

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}
EOF

    # Create certbot directory
    mkdir -p certbot/www
    
    # Restart Nginx to apply configuration
    echo -e "${YELLOW}Restarting Nginx to apply configuration...${NC}"
    docker-compose restart nginx
    
    # Obtain SSL certificate
    echo -e "${YELLOW}Obtaining SSL certificate for ${DOMAIN}...${NC}"
    certbot certonly --webroot -w certbot/www -d ${DOMAIN} --email admin@trainingclub.ch --agree-tos --non-interactive
    
    # Check if certificate was obtained successfully
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to obtain SSL certificate.${NC}"
        exit 1
    fi
    
    # Copy certificates to Nginx SSL directory
    echo -e "${YELLOW}Copying certificates to Nginx SSL directory...${NC}"
    cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem nginx/ssl/${DOMAIN}.crt
    cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem nginx/ssl/${DOMAIN}.key
    
    # Create final Nginx configuration with SSL
    echo -e "${YELLOW}Creating final Nginx configuration with SSL...${NC}"
    cat > nginx/conf/default.conf << EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN};

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${DOMAIN};

    ssl_certificate /etc/nginx/ssl/${DOMAIN}.crt;
    ssl_certificate_key /etc/nginx/ssl/${DOMAIN}.key;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    
    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    
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
    
    # Restart Nginx to apply SSL configuration
    echo -e "${YELLOW}Restarting Nginx to apply SSL configuration...${NC}"
    docker-compose restart nginx
    
    # Update .env file with domain name
    echo -e "${YELLOW}Updating .env file with domain name...${NC}"
    if grep -q "DOMAIN_NAME=" .env; then
        sed -i "s/DOMAIN_NAME=.*/DOMAIN_NAME=${DOMAIN}/" .env
    else
        echo "DOMAIN_NAME=${DOMAIN}" >> .env
    fi
    
    if grep -q "ENABLE_SSL=" .env; then
        sed -i "s/ENABLE_SSL=.*/ENABLE_SSL=true/" .env
    else
        echo "ENABLE_SSL=true" >> .env
    fi
    
    # Set up automatic renewal
    echo -e "${YELLOW}Setting up automatic renewal...${NC}"
    (crontab -l 2>/dev/null; echo "0 3 * * * /path/to/fitness-platform/ssl_domain.sh renew") | crontab -
    
    echo -e "${GREEN}SSL and domain configuration completed successfully!${NC}"
    echo -e "Your platform is now accessible at: ${YELLOW}https://${DOMAIN}${NC}"
}

# Function to renew SSL certificates
function renew_ssl {
    echo -e "${YELLOW}Renewing SSL certificates...${NC}"
    
    # Check prerequisites
    check_docker
    check_certbot
    
    # Renew certificates
    certbot renew --quiet
    
    # Check if any certificates were renewed
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to renew SSL certificates.${NC}"
        exit 1
    fi
    
    # Update certificates for all domains in nginx/ssl
    for cert in nginx/ssl/*.crt; do
        if [ -f "$cert" ]; then
            DOMAIN=$(basename "$cert" .crt)
            echo -e "${YELLOW}Updating certificates for ${DOMAIN}...${NC}"
            cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem nginx/ssl/${DOMAIN}.crt
            cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem nginx/ssl/${DOMAIN}.key
        fi
    done
    
    # Restart Nginx to apply new certificates
    echo -e "${YELLOW}Restarting Nginx to apply new certificates...${NC}"
    docker-compose restart nginx
    
    echo -e "${GREEN}SSL certificates renewed successfully!${NC}"
}

# Function to check SSL certificate status
function check_ssl_status {
    echo -e "${YELLOW}Checking SSL certificate status...${NC}"
    
    # Check prerequisites
    check_domain
    
    # Check if certificate exists
    if [ ! -f "nginx/ssl/${DOMAIN}.crt" ]; then
        echo -e "${RED}Error: SSL certificate for ${DOMAIN} not found.${NC}"
        exit 1
    fi
    
    # Check certificate expiration
    EXPIRY=$(openssl x509 -enddate -noout -in nginx/ssl/${DOMAIN}.crt | cut -d= -f2)
    EXPIRY_SECONDS=$(date -d "${EXPIRY}" +%s)
    CURRENT_SECONDS=$(date +%s)
    DAYS_LEFT=$(( (EXPIRY_SECONDS - CURRENT_SECONDS) / 86400 ))
    
    echo -e "Domain: ${GREEN}${DOMAIN}${NC}"
    echo -e "Certificate expiry date: ${GREEN}${EXPIRY}${NC}"
    echo -e "Days until expiration: ${GREEN}${DAYS_LEFT}${NC}"
    
    if [ $DAYS_LEFT -lt 30 ]; then
        echo -e "${YELLOW}Warning: Certificate will expire in less than 30 days.${NC}"
        echo -e "Run '${YELLOW}$0 renew${NC}' to renew the certificate."
    fi
}

# Main script execution
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

COMMAND=$1
DOMAIN=$2

case "$COMMAND" in
    setup)
        setup_ssl_domain
        ;;
    renew)
        renew_ssl
        ;;
    status)
        check_ssl_status
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
