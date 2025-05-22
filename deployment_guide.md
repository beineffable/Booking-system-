# Deployment and Payment Integration Guide

## Server Deployment

### Option 1: Cloud Provider (Recommended)

#### AWS Deployment
1. Create an AWS account if you don't have one
2. Launch an EC2 instance:
   - Select Ubuntu Server 22.04 LTS
   - Choose t2.medium or larger (2+ vCPUs, 4+ GB RAM)
   - Configure security groups to allow HTTP (80), HTTPS (443), and SSH (22)
   - Create and download your key pair

3. Connect to your instance:
   ```bash
   chmod 400 your-key-pair.pem
   ssh -i your-key-pair.pem ubuntu@your-instance-public-dns
   ```

4. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv nginx mysql-server
   ```

5. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/fitness-platform.git
   cd fitness-platform
   ```

6. Set up the backend:
   ```bash
   cd backend/fitness_backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

7. Configure the database:
   ```bash
   sudo mysql_secure_installation
   sudo mysql -u root -p
   ```

   In MySQL prompt:
   ```sql
   CREATE DATABASE fitness_platform;
   CREATE USER 'fitness_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON fitness_platform.* TO 'fitness_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

8. Create environment file:
   ```bash
   nano .env
   ```

   Add the following:
   ```
   DB_USERNAME=fitness_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=fitness_platform
   JWT_SECRET_KEY=your_secret_key
   STRIPE_API_KEY=your_stripe_api_key
   TWINT_MERCHANT_ID=your_twint_merchant_id
   MANUS_API_KEY=your_manus_api_key
   ```

9. Set up Nginx:
   ```bash
   sudo nano /etc/nginx/sites-available/fitness-platform
   ```

   Add the following configuration:
   ```
   server {
       listen 80;
       server_name your-domain.com;

       location /api {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

   Enable the site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/fitness-platform /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl restart nginx
   ```

10. Set up SSL with Let's Encrypt:
    ```bash
    sudo apt install certbot python3-certbot-nginx
    sudo certbot --nginx -d your-domain.com
    ```

11. Set up the frontend:
    ```bash
    cd ../../frontend/fitness_frontend
    npm install
    npm run build
    ```

12. Create systemd service for the backend:
    ```bash
    sudo nano /etc/systemd/system/fitness-backend.service
    ```

    Add the following:
    ```
    [Unit]
    Description=Fitness Platform Backend
    After=network.target

    [Service]
    User=ubuntu
    WorkingDirectory=/home/ubuntu/fitness-platform/backend/fitness_backend
    Environment="PATH=/home/ubuntu/fitness-platform/backend/fitness_backend/venv/bin"
    ExecStart=/home/ubuntu/fitness-platform/backend/fitness_backend/venv/bin/python -m flask run --host=0.0.0.0
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

    Enable and start the service:
    ```bash
    sudo systemctl enable fitness-backend
    sudo systemctl start fitness-backend
    ```

### Option 2: Shared Hosting

If you prefer shared hosting:

1. Check if your hosting provider supports Python/Flask applications
2. Upload the backend and frontend code via FTP
3. Set up a MySQL database through your hosting control panel
4. Configure environment variables through your hosting control panel
5. Follow hosting-specific instructions for deploying Flask applications

## Payment Integration

### Stripe Integration

1. Create a Stripe account:
   - Go to [stripe.com](https://stripe.com) and sign up
   - Complete the verification process

2. Get your API keys:
   - In the Stripe Dashboard, go to Developers > API keys
   - Note both the Publishable key and Secret key

3. Configure payment methods:
   - Go to Settings > Payment methods
   - Enable credit cards, Apple Pay, and Google Pay
   - Configure any additional payment methods you want to offer

4. Set up webhooks:
   - Go to Developers > Webhooks
   - Add an endpoint: `https://your-domain.com/api/payment/webhook`
   - Select events to listen for: `payment_intent.succeeded`, `payment_intent.failed`, `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`

5. Configure products and prices:
   - Go to Products > Add product
   - Create products for each membership type
   - Set up pricing for each product (one-time or recurring)

6. Update the platform configuration:
   - Log in to your fitness platform as admin
   - Go to System Configuration > Integrations
   - Enter your Stripe API keys
   - Enable Stripe integration

### Twint Integration (for Swiss Payments)

1. Contact Twint for merchant integration:
   - Visit [twint.ch](https://www.twint.ch) for business integration
   - Complete the merchant application process

2. Receive your merchant credentials:
   - Merchant ID
   - API key
   - Integration documentation

3. Update the platform configuration:
   - Log in to your fitness platform as admin
   - Go to System Configuration > Integrations
   - Enter your Twint merchant credentials
   - Enable Twint integration

## Platform Configuration

### Initial Admin Setup

1. Access the admin console:
   - Go to `https://your-domain.com/admin`
   - Log in with default credentials:
     - Email: admin@trainingclub.ch
     - Password: TrainingClub2025! (change immediately)

2. Change admin password:
   - Go to Profile > Security
   - Update your password to a strong, unique password

3. Configure general settings:
   - Go to System Configuration > General
   - Update site name: "Training Club"
   - Set contact email to your business email
   - Set timezone to "Europe/Zurich"
   - Configure other general settings as needed

4. Configure appearance:
   - Go to System Configuration > Appearance
   - Set primary color to #9ed6fe
   - Set secondary color to #f16c13
   - Set neutral color to #c8b4a3
   - Upload your logo (recommended size: 200x60px)
   - Add any custom CSS if needed

5. Configure notifications:
   - Go to System Configuration > Notifications
   - Enable email notifications
   - Set reminder hours before class (recommended: 24)
   - Configure SMS notifications if desired

### Membership Setup

1. Create membership types:
   - Go to Admin > Memberships > Add New
   - Create each membership type (Standard, Premium, etc.)
   - Set pricing, duration, and features for each

2. Configure class types:
   - Go to Admin > Classes > Class Types
   - Add your different class types (HIIT, Yoga, Strength, etc.)
   - Set default capacity and duration for each

3. Set up trainers:
   - Go to Admin > Users > Add New
   - Create accounts for each trainer
   - Assign appropriate permissions

## Website Integration

### Embedding Options

#### Option 1: iFrame Embedding
Add this code to your website where you want the platform to appear:

```html
<iframe 
  src="https://your-domain.com" 
  style="width:100%; height:800px; border:none;"
  title="Training Club Fitness Platform">
</iframe>
```

#### Option 2: JavaScript Snippet
Add this code to your website:

```html
<div id="training-club-platform"></div>
<script src="https://your-domain.com/embed.js"></script>
<script>
  TrainingClubPlatform.init({
    container: '#training-club-platform',
    theme: 'light',
    defaultView: 'schedule'
  });
</script>
```

#### Option 3: Replace "Book Now" Button
Update your existing "Book Now" button to link to the platform:

```html
<a href="https://your-domain.com" class="book-now-button">Book Now</a>
```

### Testing the Integration

1. Test on desktop and mobile devices
2. Verify that styling matches your website
3. Test the user journey from your website to booking a class
4. Test payment processing with test cards

## Payment Testing

### Stripe Test Mode

1. Ensure you're in test mode in Stripe dashboard
2. Use these test card numbers:
   - Successful payment: 4242 4242 4242 4242
   - Failed payment: 4000 0000 0000 0002
   - 3D Secure required: 4000 0027 6000 3184
3. Use any future expiration date and any 3-digit CVC
4. Use any name and postal code

### Testing the Full Payment Flow

1. Create a test membership purchase:
   - Log in as a test member
   - Select a membership plan
   - Proceed to checkout
   - Use a test card number
   - Verify the payment success/failure handling

2. Test class booking:
   - Log in as a test member
   - Book a class
   - Verify that credits are deducted or payment is processed
   - Check confirmation emails

3. Test membership cancellation:
   - Log in as a test member
   - Cancel a membership
   - Verify the cancellation process
   - Check confirmation emails

## Going Live

When you're ready to accept real payments:

1. Switch to live mode in Stripe dashboard
2. Update your API keys in the platform configuration
3. Process a small real payment to verify everything works
4. Monitor the first few transactions closely

## Troubleshooting

### Common Issues

1. Payment failures:
   - Check Stripe dashboard for error messages
   - Verify API keys are correct
   - Check webhook configuration

2. Integration issues:
   - Check browser console for JavaScript errors
   - Verify CORS settings if embedding on a different domain
   - Check network requests for API errors

3. Email notification issues:
   - Verify SMTP settings
   - Check spam filters
   - Test email delivery with a service like Mailgun

### Getting Help

If you encounter issues:

1. Check the platform documentation
2. Review error logs on your server
3. Contact technical support at support@trainingclub.ch

## Security Considerations

1. Regularly update your server and dependencies
2. Enable two-factor authentication for admin accounts
3. Regularly backup your database
4. Monitor for suspicious activity
5. Conduct periodic security reviews

## Next Steps

After initial setup:

1. Train your staff on using the platform
2. Create a communication plan for members
3. Consider a phased rollout to test with a subset of members
4. Gather feedback and make adjustments as needed
