# AMU Pay EC2 Deployment Guide

This guide will help you deploy the AMU Pay Django application on Amazon EC2.

## Prerequisites

1. An AWS EC2 instance (Ubuntu 22.04 LTS recommended)
2. Security Group configured to allow:
   - SSH (port 22)
   - HTTP (port 80)
   - HTTPS (port 443) - if using SSL
   - Custom TCP (port 8000) - for direct access if needed
3. Elastic IP address (recommended for static IP)
4. Domain name (optional, for production)

## Step 1: Initial EC2 Setup

### 1.1 Connect to your EC2 instance

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 1.2 Update system packages

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

## Step 2: Transfer Project Files

### Option A: Using SCP (from your local machine)

```bash
scp -i your-key.pem -r amu_pay13.1/* ubuntu@your-ec2-ip:/home/ubuntu/amu_pay/
```

### Option B: Using Git (recommended)

```bash
# On EC2 instance
cd /home/ubuntu
git clone your-repository-url amu_pay
cd amu_pay
```

## Step 3: Run Setup Script

```bash
cd /home/ubuntu/amu_pay
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Install Python 3.11 and required system packages
- Install MySQL client libraries
- Install Nginx
- Create virtual environment
- Install Python dependencies
- Set up directories and permissions
- Configure Nginx
- Set up systemd service

## Step 4: Configure Environment Variables

Copy the example environment file and edit it with your actual configuration:

```bash
cp env.example .env
nano .env
```

Required variables:
- `SECRET_KEY`: Generate a new secret key for production
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Add your domain name and EC2 public IP
- Database credentials
- Email configuration
- Twilio credentials
- AI API keys (Pinecone, Gemini)

### Generate a new SECRET_KEY:

```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## Step 5: Database Setup

### Option A: Using Amazon RDS (Recommended for Production)

Your RDS instance is already configured:
- **Endpoint:** `amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com`
- **Port:** `3306`

**Follow the detailed RDS setup guide:** See `RDS_SETUP.md` for complete instructions.

**Quick setup:**
1. Update `.env` with RDS credentials:
   ```env
   DB_HOST=amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com
   DB_PORT=3306
   DB_NAME=amu_pay_db
   DB_USER=your-rds-username
   DB_PASSWORD=your-rds-password
   DB_USE_SSL=True
   ```

2. Configure RDS Security Group to allow connections from your EC2 instance

3. Create database and user in RDS (see RDS_SETUP.md)

4. Test connection:
   ```bash
   python test_rds_connection.py
   ```

### Option B: Local MySQL

```bash
sudo mysql_secure_installation
sudo mysql -u root -p
```

```sql
CREATE DATABASE amu_pay_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'amu_pay_user'@'localhost' IDENTIFIED BY 'your-password';
GRANT ALL PRIVILEGES ON amu_pay_db.* TO 'amu_pay_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## Step 6: Run Migrations and Create Superuser

```bash
cd /home/ubuntu/amu_pay
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## Step 7: Start Services

### Start Django application:

```bash
sudo systemctl start amu_pay
sudo systemctl enable amu_pay  # Enable on boot
sudo systemctl status amu_pay  # Check status
```

### Start Nginx:

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx
```

## Step 8: Configure Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Step 9: SSL Certificate (Optional but Recommended)

### Using Let's Encrypt with Certbot:

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

Certbot will automatically configure Nginx for HTTPS.

## Step 10: Verify Deployment

1. Check application logs:
   ```bash
   sudo journalctl -u amu_pay -f
   ```

2. Check Nginx logs:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   sudo tail -f /var/log/nginx/access.log
   ```

3. Test the application:
   - Visit `http://your-ec2-ip` or `http://your-domain.com`
   - Check health endpoint: `http://your-ec2-ip/health/`

## Deployment Updates

For future deployments, use the deploy script:

```bash
cd /home/ubuntu/amu_pay
chmod +x deploy.sh
./deploy.sh
```

Or manually:

```bash
cd /home/ubuntu/amu_pay
source venv/bin/activate
git pull  # If using git
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart amu_pay
sudo systemctl reload nginx
```

## Docker Deployment (Alternative)

If you prefer Docker deployment:

1. Install Docker and Docker Compose:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. Configure `.env` file

3. Build and run:
   ```bash
   docker-compose up -d --build
   ```

## Troubleshooting

### Application not starting:

```bash
# Check service status
sudo systemctl status amu_pay

# Check logs
sudo journalctl -u amu_pay -n 50

# Check if port is in use
sudo netstat -tulpn | grep 8000
```

### Database connection issues:

```bash
# Test MySQL connection
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME
```

### Static files not loading:

```bash
# Recollect static files
python manage.py collectstatic --noinput

# Check permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/amu_pay/staticfiles
```

### Nginx errors:

```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log
```

## Security Recommendations

1. **Firewall**: Use AWS Security Groups and UFW
2. **SSL**: Always use HTTPS in production
3. **Secrets**: Never commit `.env` file to version control
4. **Updates**: Regularly update system packages
5. **Backups**: Set up automated database backups
6. **Monitoring**: Set up CloudWatch or similar monitoring
7. **Rate Limiting**: Consider implementing rate limiting for API endpoints

## Backup and Recovery

### Database Backup:

```bash
mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > backup_$(date +%Y%m%d).sql
```

### Media Files Backup:

```bash
tar -czf media_backup_$(date +%Y%m%d).tar.gz /home/ubuntu/amu_pay/media/
```

## Monitoring

Consider setting up:
- AWS CloudWatch for server metrics
- Application monitoring (Sentry, New Relic, etc.)
- Database monitoring
- Uptime monitoring

## Support

For issues or questions, check:
- Application logs: `sudo journalctl -u amu_pay`
- Nginx logs: `/var/log/nginx/`
- Gunicorn logs: `/var/log/gunicorn/`

