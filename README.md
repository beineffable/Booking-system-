# Training Club Fitness Platform - Deployment Automation Package

## Overview

This package contains a complete automated deployment solution for the Training Club Fitness Platform. It provides a Docker-based containerized architecture with one-command deployment, automated SSL configuration, and comprehensive CI/CD integration.

## Package Contents

1. **Docker Configuration**
   - `docker_architecture.md` - Architecture design and specifications
   - `backend/fitness_backend/Dockerfile` - Backend container configuration
   - `frontend/fitness_frontend/Dockerfile` - Frontend container configuration
   - `docker-compose.yml` - Multi-container orchestration

2. **Deployment Scripts**
   - `deploy.sh` - Main deployment script for one-command setup
   - `ssl_domain.sh` - SSL certificate and domain configuration
   - `rollback_update.sh` - Version management and rollback functionality
   - `test_local_deployment.sh` - Local deployment testing

3. **Database Configuration**
   - `db/init/01-schema.sql` - Database schema and seed data

4. **Environment Configuration**
   - `.env.example` - Example environment variables

5. **CI/CD Pipeline**
   - `.github/workflows/ci-cd.yml` - GitHub Actions workflow

6. **Documentation**
   - `deployment_documentation.md` - Comprehensive deployment guide
   - `custom_fitness_platform_plan.md` - Platform overview
   - `feature_prioritization.md` - Feature breakdown
   - `system_architecture.md` - System architecture
   - `technology_stack.md` - Technology recommendations
   - `project_timeline.md` - Implementation timeline
   - `wireframes_and_ui_mockups.md` - Visual representations
   - `database_schema_and_user_roles.md` - Data structure
   - `payment_integration_plan.md` - Payment processing
   - `admin_console_and_permissions.md` - Admin tools
   - `member_and_trainer_portals.md` - User interfaces
   - `leaderboard_and_analytics.md` - Performance tracking
   - `apple_style_design_guidelines.md` - Design specifications
   - `requirements_validation.md` - Requirements verification
   - `manus_integration.md` - Manus account integration
   - `advanced_features_plan.md` - Advanced features
   - `competitive_analysis.md` - Competitor comparison
   - `feature_enhancements.md` - Platform improvements

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/trainingclub/fitness-platform.git
   cd fitness-platform
   ```

2. Make deployment scripts executable:
   ```bash
   chmod +x deploy.sh ssl_domain.sh rollback_update.sh test_local_deployment.sh
   ```

3. Initialize the platform:
   ```bash
   ./deploy.sh init
   ```

4. Access the platform:
   - Web interface: http://localhost
   - Admin panel: http://localhost/admin
   - Default admin credentials:
     - Email: admin@trainingclub.ch
     - Password: TrainingClub2025!

## Deployment Options

### Local Development

For local development and testing:
```bash
./deploy.sh start
```

### Production Deployment

For production deployment with SSL:
```bash
./ssl_domain.sh setup yourdomain.com
./deploy.sh start
```

### CI/CD Deployment

For automated deployment via GitHub Actions:
1. Configure repository secrets
2. Push to the appropriate branch
3. GitHub Actions will handle the deployment

## Support

For additional support or questions, please contact support@trainingclub.ch.
