# Docker Deployment Architecture

## Overview

This document outlines the Docker architecture for automating the deployment of the Training Club Fitness Platform. The architecture is designed to be scalable, maintainable, and easy to deploy in various environments.

## Architecture Components

### 1. Docker Containers

The application will be split into the following containers:

1. **Backend Container**
   - Flask application
   - Python 3.11
   - Application dependencies
   - Gunicorn WSGI server

2. **Frontend Container**
   - React application
   - Node.js runtime
   - Nginx for serving static files
   - Build artifacts

3. **Database Container**
   - MySQL 8.0
   - Persistent volume for data storage
   - Initialization scripts

4. **Redis Container**
   - For caching and session management
   - Improves application performance

5. **Nginx Proxy Container**
   - Reverse proxy for routing requests
   - SSL termination
   - Load balancing

### 2. Container Relationships

```
                   ┌─────────────┐
                   │             │
                   │  Nginx      │
                   │  Proxy      │
                   │             │
                   └─────┬───────┘
                         │
                         ▼
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────┐             ┌─────────────────┐
│                 │             │                 │
│  Frontend       │             │  Backend        │
│  Container      │             │  Container      │
│                 │             │                 │
└─────────────────┘             └────────┬────────┘
                                         │
                                         ▼
                               ┌─────────────────────┐
                               │                     │
                               │  Redis              │
                               │  Container          │
                               │                     │
                               └─────────────────────┘
                                         │
                                         ▼
                               ┌─────────────────────┐
                               │                     │
                               │  Database           │
                               │  Container          │
                               │                     │
                               └─────────────────────┘
```

## Container Specifications

### Backend Container

- **Base Image**: python:3.11-slim
- **Exposed Port**: 5000
- **Environment Variables**:
  - `FLASK_APP`
  - `FLASK_ENV`
  - `DB_USERNAME`
  - `DB_PASSWORD`
  - `DB_HOST`
  - `DB_PORT`
  - `DB_NAME`
  - `JWT_SECRET_KEY`
  - `STRIPE_API_KEY`
  - `TWINT_MERCHANT_ID`
  - `MANUS_API_KEY`
  - `REDIS_URL`
- **Volumes**:
  - `/app/uploads` for user-uploaded files
- **Health Check**: HTTP GET on `/api/health`

### Frontend Container

- **Build Stage**:
  - **Base Image**: node:20-alpine
  - Build React application
- **Runtime Stage**:
  - **Base Image**: nginx:alpine
  - Copy build artifacts from build stage
  - Custom nginx configuration
- **Exposed Port**: 80
- **Environment Variables**:
  - `REACT_APP_API_URL`
  - `REACT_APP_STRIPE_PUBLIC_KEY`
- **Health Check**: HTTP GET on `/`

### Database Container

- **Base Image**: mysql:8.0
- **Exposed Port**: 3306
- **Environment Variables**:
  - `MYSQL_ROOT_PASSWORD`
  - `MYSQL_DATABASE`
  - `MYSQL_USER`
  - `MYSQL_PASSWORD`
- **Volumes**:
  - `/var/lib/mysql` for persistent data storage
  - `/docker-entrypoint-initdb.d` for initialization scripts
- **Health Check**: MySQL connection check

### Redis Container

- **Base Image**: redis:alpine
- **Exposed Port**: 6379
- **Volumes**:
  - `/data` for persistent cache storage
- **Health Check**: Redis ping command

### Nginx Proxy Container

- **Base Image**: nginx:alpine
- **Exposed Ports**: 80, 443
- **Volumes**:
  - `/etc/nginx/conf.d` for configuration
  - `/etc/letsencrypt` for SSL certificates
- **Health Check**: HTTP GET on `/health`

## Network Configuration

- All containers will be on the same Docker network
- Internal communication uses container names as hostnames
- Only the Nginx proxy container exposes ports to the host

## Volume Management

- Named volumes for persistent data
- Bind mounts for configuration files
- Temporary volumes for build artifacts

## Security Considerations

- No sensitive information in Dockerfiles
- All credentials passed via environment variables
- Principle of least privilege for container permissions
- Regular security updates for base images

## Scaling Strategy

- Horizontal scaling for backend and frontend containers
- Database replication for high availability
- Redis cluster for distributed caching

## Development vs. Production

- Development:
  - Hot reloading for frontend
  - Debug mode for backend
  - Local database with sample data

- Production:
  - Optimized builds
  - Minimized images
  - Production-grade database configuration
  - SSL encryption

## Next Steps

1. Create Dockerfiles for each component
2. Develop docker-compose.yml for local development
3. Configure CI/CD pipeline for automated builds
4. Implement deployment scripts for various environments
