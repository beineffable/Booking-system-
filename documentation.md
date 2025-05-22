# Training Club Fitness Platform Documentation

## Overview

The Training Club Fitness Platform is a comprehensive membership management solution designed to replace Gloflox with enhanced features and customization options. This platform addresses all the limitations of Gloflox while adding significant improvements in user experience, automation, payment processing, and analytics.

## Key Features

### Member Features
- Self-service membership management (including cancellations)
- Class scheduling and booking
- Class check-in functionality
- Credits/token system
- Friend referral program
- Access to class photos with secure code system
- Personal fitness tracking and metrics

### Trainer Features
- Class management and scheduling
- Attendance tracking
- Member performance monitoring
- Photo upload for class participants
- Communication tools for member engagement

### Admin Features
- Comprehensive dashboard with real-time analytics
- User management with granular permissions
- System configuration and customization
- Sales analytics and conversion optimization
- Manus integration for direct code editing and email drafting
- Advanced reporting on retention, attendance, and revenue

### Payment Integration
- Stripe integration for global payments
- Twint integration for Swiss customers
- Flexible membership and pricing options

## Technical Architecture

The platform is built using a modern tech stack:

### Backend
- Flask (Python) for the API server
- SQLAlchemy for database ORM
- JWT for authentication
- RESTful API design

### Frontend
- React with TypeScript
- Material-UI component library
- Responsive design for mobile and desktop
- Apple-inspired aesthetics

### Integrations
- Stripe API for payment processing
- Twint API for Swiss payment methods
- Manus API for code editing and email drafting

## Installation and Deployment

### Prerequisites
- Python 3.11+
- Node.js 20+
- MySQL or PostgreSQL database

### Backend Setup
1. Navigate to `/fitness_platform/backend/fitness_backend`
2. Activate the virtual environment: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Configure environment variables (see Configuration section)
5. Run the server: `python -m flask run --host=0.0.0.0`

### Frontend Setup
1. Navigate to `/fitness_platform/frontend/fitness_frontend`
2. Install dependencies: `npm install`
3. Configure API endpoint in `.env` file
4. Run the development server: `npm start`

### Production Deployment
For production deployment, the platform can be:
1. Deployed as standalone web application
2. Embedded into the existing trainingclub.ch website
3. Packaged as mobile applications for iOS and Android

## Configuration

### Environment Variables
- `DB_USERNAME`: Database username
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port
- `DB_NAME`: Database name
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `STRIPE_API_KEY`: Stripe API key
- `TWINT_MERCHANT_ID`: Twint merchant ID
- `MANUS_API_KEY`: Manus API key

### System Configuration
The platform includes a comprehensive admin configuration panel for:
- General settings (site name, contact email, timezone)
- Appearance settings (colors, logo, custom CSS)
- Notification settings (email, SMS)
- Integration settings (payment gateways, Manus)

## User Roles and Permissions

### Member
- View and book classes
- Manage personal profile
- Track attendance and progress
- Participate in referral program
- Use and gift credits
- Access class photos with code

### Trainer
- Manage assigned classes
- Track member attendance
- Upload class photos
- View member performance
- Communicate with members

### Admin
- Full system configuration
- User management
- Financial reporting
- Analytics and optimization
- Integration with Manus for code editing

## Embedding Instructions

The platform is designed to be seamlessly embedded into the existing trainingclub.ch website:

### iFrame Embedding
```html
<iframe 
  src="https://fitness-platform.trainingclub.ch" 
  style="width:100%; height:800px; border:none;"
  title="Training Club Fitness Platform">
</iframe>
```

### JavaScript Snippet
```javascript
<div id="training-club-platform"></div>
<script src="https://fitness-platform.trainingclub.ch/embed.js"></script>
<script>
  TrainingClubPlatform.init({
    container: '#training-club-platform',
    theme: 'light',
    defaultView: 'schedule'
  });
</script>
```

## Mobile Applications

The platform includes responsive web design for mobile browsers and can be extended with native mobile applications:

### iOS App
- Apple-inspired design
- Native iOS components
- Push notifications
- Touch/Face ID authentication

### Android App
- Material Design
- Native Android components
- Push notifications
- Biometric authentication

## Data Security and Compliance

The platform is designed with security and privacy in mind:

- GDPR compliant data collection and processing
- Secure data storage with encryption
- Regular security audits
- Data export and deletion capabilities
- Consent management for marketing and photos

## Customization

The platform supports extensive customization:

- Branding (colors, logo, fonts)
- Email templates
- Membership types and pricing
- Class categories and schedules
- Custom fields for member profiles

## Support and Maintenance

### Technical Support
- Documentation and knowledge base
- Email support
- Bug reporting system

### Maintenance
- Regular security updates
- Feature enhancements
- Performance optimization

## Future Roadmap

Planned future enhancements:

- Advanced fitness tracking with wearable integration
- Nutrition planning and tracking
- Community features and social sharing
- Virtual classes and content delivery
- AI-powered workout recommendations

## Conclusion

The Training Club Fitness Platform provides a comprehensive solution for membership management, class scheduling, payment processing, and analytics. With its modern design, extensive customization options, and advanced features, it significantly improves upon the limitations of Gloflox while maintaining the aesthetic and branding of Training Club.
