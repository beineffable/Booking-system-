# Automated Deployment Documentation

## Overview

This document provides comprehensive instructions for deploying the Training Club Fitness Platform using the automated deployment solution. The platform is containerized with Docker and can be deployed with a single command in both development and production environments.

## Prerequisites

Before deploying the platform, ensure you have the following prerequisites installed:

1. **Docker** (version 20.10.0 or higher)
   - Installation instructions: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)

2. **Docker Compose** (version 2.0.0 or higher)
   - Installation instructions: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

3. **Git** (for version control and updates)
   - Installation instructions: [https://git-scm.com/downloads](https://git-scm.com/downloads)

4. **Bash** (for running deployment scripts)
   - Pre-installed on most Linux distributions and macOS
   - For Windows, use Git Bash or WSL

## Getting Started

### Initial Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/trainingclub/fitness-platform.git
   cd fitness-platform
   ```

2. Create environment configuration:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file with your specific configuration:
   ```bash
   nano .env
   ```

   Be sure to update:
   - Database credentials
   - JWT secret key
   - Stripe and Twint API keys
   - SMTP settings for email notifications
   - Domain name

4. Initialize the platform:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh init
   ```

   This command will:
   - Create necessary directories
   - Configure Nginx
   - Build and start all containers
   - Initialize the database with schema and seed data

5. Access the platform:
   - Web interface: http://localhost
   - Admin panel: http://localhost/admin
   - Default admin credentials:
     - Email: admin@trainingclub.ch
     - Password: TrainingClub2025!

### Deployment Commands

The `deploy.sh` script provides several commands for managing the platform:

#### Basic Commands

- **Initialize the platform**:
  ```bash
  ./deploy.sh init
  ```

- **Start all services**:
  ```bash
  ./deploy.sh start
  ```

- **Stop all services**:
  ```bash
  ./deploy.sh stop
  ```

- **Restart all services**:
  ```bash
  ./deploy.sh restart
  ```

- **View logs from all services**:
  ```bash
  ./deploy.sh logs
  ```

- **Check status of all services**:
  ```bash
  ./deploy.sh status
  ```

#### Advanced Commands

- **Build or rebuild services**:
  ```bash
  ./deploy.sh build
  ```

- **Update all services** (pull latest code and rebuild):
  ```bash
  ./deploy.sh update
  ```

- **Backup database**:
  ```bash
  ./deploy.sh backup
  ```

- **Restore database from backup**:
  ```bash
  ./deploy.sh restore
  ```

- **Show help message**:
  ```bash
  ./deploy.sh help
  ```

## Deployment Environments

### Local Development

For local development, the platform is configured to run on localhost with default ports:

- Web interface: http://localhost
- Backend API: http://localhost/api
- Database: localhost:3306 (not exposed by default)
- Redis: localhost:6379 (not exposed by default)

### Staging Environment

For staging deployment, follow these steps:

1. Set up a staging server with Docker and Docker Compose installed
2. Configure the CI/CD pipeline with staging server credentials
3. Push changes to the `develop` branch or manually trigger the workflow
4. The platform will be deployed to the staging server automatically

### Production Environment

For production deployment, follow these steps:

1. Set up a production server with Docker and Docker Compose installed
2. Configure the CI/CD pipeline with production server credentials
3. Manually trigger the workflow with the `production` environment selected
4. The platform will be deployed to the production server automatically

## CI/CD Pipeline

The platform includes a GitHub Actions workflow for continuous integration and deployment:

1. **Test**: Runs backend and frontend tests
2. **Build**: Builds Docker images and pushes them to Docker Hub
3. **Deploy**: Deploys the platform to staging or production environment

To configure the CI/CD pipeline:

1. Add the following secrets to your GitHub repository:
   - `DOCKERHUB_USERNAME`: Docker Hub username
   - `DOCKERHUB_TOKEN`: Docker Hub access token
   - `STAGING_HOST`: Staging server hostname or IP
   - `STAGING_USERNAME`: Staging server SSH username
   - `STAGING_SSH_KEY`: Staging server SSH private key
   - `PRODUCTION_HOST`: Production server hostname or IP
   - `PRODUCTION_USERNAME`: Production server SSH username
   - `PRODUCTION_SSH_KEY`: Production server SSH private key
   - Database credentials and API keys for each environment

2. Push changes to the repository:
   - Pushing to `develop` branch deploys to staging
   - Manually triggering the workflow deploys to production

## Directory Structure

The platform follows this directory structure:

```
fitness-platform/
├── backend/                # Backend Flask application
│   └── fitness_backend/
│       ├── src/            # Application source code
│       ├── venv/           # Python virtual environment
│       ├── Dockerfile      # Backend Docker configuration
│       └── requirements.txt # Python dependencies
├── frontend/               # Frontend React application
│   └── fitness_frontend/
│       ├── src/            # Application source code
│       ├── public/         # Static assets
│       ├── build/          # Production build
│       └── Dockerfile      # Frontend Docker configuration
├── db/                     # Database configuration
│   └── init/               # Initialization scripts
├── nginx/                  # Nginx configuration
│   ├── conf/               # Configuration files
│   ├── ssl/                # SSL certificates
│   └── www/                # Static files
├── backups/                # Database backups
├── .github/                # GitHub Actions workflows
├── docker-compose.yml      # Docker Compose configuration
├── .env.example            # Example environment variables
├── .env                    # Environment variables (not in version control)
├── deploy.sh               # Deployment script
└── test_local_deployment.sh # Local deployment test script
```

## Environment Variables

The platform uses environment variables for configuration. These are stored in the `.env` file, which should not be committed to version control.

Key environment variables include:

- **Database Configuration**:
  - `DB_USERNAME`: Database username
  - `DB_PASSWORD`: Database password
  - `DB_NAME`: Database name
  - `MYSQL_ROOT_PASSWORD`: MySQL root password

- **Security**:
  - `JWT_SECRET_KEY`: Secret key for JWT token generation

- **API Keys**:
  - `STRIPE_API_KEY`: Stripe API key
  - `STRIPE_WEBHOOK_SECRET`: Stripe webhook secret
  - `TWINT_MERCHANT_ID`: Twint merchant ID
  - `TWINT_API_KEY`: Twint API key
  - `MANUS_API_KEY`: Manus API key

- **Frontend Configuration**:
  - `REACT_APP_API_URL`: Backend API URL
  - `REACT_APP_STRIPE_PUBLIC_KEY`: Stripe publishable key

- **Email Configuration**:
  - `SMTP_HOST`: SMTP server hostname
  - `SMTP_PORT`: SMTP server port
  - `SMTP_USERNAME`: SMTP username
  - `SMTP_PASSWORD`: SMTP password
  - `SMTP_FROM_EMAIL`: From email address

## Customization

### Nginx Configuration

To customize the Nginx configuration:

1. Edit the configuration file:
   ```bash
   nano nginx/conf/default.conf
   ```

2. Restart the Nginx container:
   ```bash
   docker-compose restart nginx
   ```

### Database Configuration

To customize the database initialization:

1. Edit the initialization script:
   ```bash
   nano db/init/01-schema.sql
   ```

2. Rebuild and restart the database container:
   ```bash
   ./deploy.sh stop
   ./deploy.sh build
   ./deploy.sh start
   ```

### Adding SSL Certificates

To add SSL certificates:

1. Place your certificates in the `nginx/ssl` directory:
   ```bash
   cp your-cert.pem nginx/ssl/cert.pem
   cp your-key.pem nginx/ssl/key.pem
   ```

2. Update the Nginx configuration to use SSL:
   ```bash
   nano nginx/conf/default.conf
   ```

   Add the following to the server block:
   ```
   listen 443 ssl;
   ssl_certificate /etc/nginx/ssl/cert.pem;
   ssl_certificate_key /etc/nginx/ssl/key.pem;
   ```

3. Restart the Nginx container:
   ```bash
   docker-compose restart nginx
   ```

## Troubleshooting

### Common Issues

1. **Container fails to start**:
   - Check container logs: `docker-compose logs [service_name]`
   - Verify environment variables in `.env` file
   - Ensure ports are not already in use

2. **Database connection issues**:
   - Check database credentials in `.env` file
   - Verify database container is running: `docker-compose ps db`
   - Check database logs: `docker-compose logs db`

3. **Nginx proxy issues**:
   - Check Nginx configuration: `docker-compose exec nginx nginx -t`
   - Verify backend and frontend containers are running
   - Check Nginx logs: `docker-compose logs nginx`

4. **SSL certificate issues**:
   - Verify certificate and key files exist in `nginx/ssl` directory
   - Check certificate validity: `openssl verify nginx/ssl/cert.pem`
   - Check Nginx configuration: `docker-compose exec nginx nginx -t`

### Viewing Logs

To view logs from all services:
```bash
./deploy.sh logs
```

To view logs from a specific service:
```bash
docker-compose logs [service_name]
```

To follow logs in real-time:
```bash
docker-compose logs -f [service_name]
```

### Restarting Services

To restart all services:
```bash
./deploy.sh restart
```

To restart a specific service:
```bash
docker-compose restart [service_name]
```

## Backup and Restore

### Creating Backups

To create a database backup:
```bash
./deploy.sh backup
```

This will create a backup file in the `backups` directory with a timestamp.

### Restoring Backups

To restore a database backup:
```bash
./deploy.sh restore
```

This will prompt you to select a backup file from the `backups` directory.

## Security Considerations

1. **Environment Variables**:
   - Never commit `.env` file to version control
   - Use strong, unique passwords for all credentials
   - Rotate API keys and secrets regularly

2. **Docker Security**:
   - Keep Docker and Docker Compose updated
   - Use non-root users in containers
   - Limit container capabilities

3. **Network Security**:
   - Use SSL/TLS for all production deployments
   - Configure firewall to restrict access to necessary ports
   - Use secure headers in Nginx configuration

4. **Database Security**:
   - Use strong passwords for database users
   - Restrict database access to necessary services
   - Regularly backup database data

## Performance Optimization

1. **Container Resources**:
   - Adjust container resource limits in `docker-compose.yml`
   - Monitor container resource usage with `docker stats`

2. **Database Optimization**:
   - Add indexes for frequently queried fields
   - Optimize database queries
   - Consider database caching

3. **Frontend Optimization**:
   - Enable gzip compression in Nginx
   - Use browser caching for static assets
   - Optimize images and assets

## Scaling

To scale the platform for higher load:

1. **Horizontal Scaling**:
   - Scale backend containers: `docker-compose up -d --scale backend=3`
   - Configure Nginx for load balancing

2. **Vertical Scaling**:
   - Increase container resource limits in `docker-compose.yml`
   - Upgrade server hardware

3. **Database Scaling**:
   - Set up database replication
   - Consider sharding for very large datasets

## Maintenance

### Regular Updates

To update the platform:
```bash
git pull
./deploy.sh update
```

### Monitoring

Monitor the platform using:
- Container health checks: `docker-compose ps`
- Container logs: `./deploy.sh logs`
- Container stats: `docker stats`

### Backups

Schedule regular backups:
```bash
# Add to crontab
0 2 * * * cd /path/to/fitness-platform && ./deploy.sh backup
```

## Conclusion

This automated deployment solution provides a streamlined way to deploy and manage the Training Club Fitness Platform. By following the instructions in this document, you can easily set up, configure, and maintain the platform in various environments.

For additional support or questions, please contact support@trainingclub.ch.
