# AMU Pay - Complete EC2 Deployment Guide

**Complete step-by-step guide for deploying AMU Pay Django application on Amazon EC2 with Amazon RDS MySQL**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [EC2 Instance Setup](#ec2-instance-setup)
3. [Transfer Project Files](#transfer-project-files)
4. [Initial Server Setup](#initial-server-setup)
5. [RDS Database Configuration](#rds-database-configuration)
6. [Application Configuration](#application-configuration)
7. [Deploy Application](#deploy-application)
8. [Configure Web Server](#configure-web-server)
9. [SSL Certificate Setup](#ssl-certificate-setup)
10. [Verification & Testing](#verification--testing)
11. [Troubleshooting](#troubleshooting)
12. [Maintenance & Updates](#maintenance--updates)

---

## Prerequisites

### AWS Resources Required

- ✅ **EC2 Instance** (Ubuntu 22.04 LTS recommended)
- ✅ **Amazon RDS MySQL Instance** (Already configured)
  - Endpoint: `amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com`
  - Port: `3306`
  - Region: `eu-north-1`
- ✅ **Security Groups** configured
- ✅ **Elastic IP** (recommended for static IP)
- ✅ **Domain Name** (optional, for production)

### EC2 Security Group Configuration

Ensure your EC2 Security Group allows:
- **SSH (22)** - From your IP
- **HTTP (80)** - From anywhere (0.0.0.0/0)
- **HTTPS (443)** - From anywhere (0.0.0.0/0)
- **Custom TCP (8000)** - From anywhere (optional, for testing)

### RDS Security Group Configuration

Your RDS Security Group (`sg-0f68aef52f442fe5e`) must allow:
- **MySQL/Aurora (3306)** - From your EC2 Security Group (recommended) or EC2 Private IP

### Required Credentials & Keys

Before starting, gather:
- [ ] EC2 SSH key pair (.pem file)
- [ ] RDS master username and password
- [ ] Gmail app password (for email)
- [ ] Twilio Account SID and Auth Token
- [ ] Twilio Phone Number and WhatsApp credentials
- [ ] Pinecone API Key (if using AI features)
- [ ] Gemini API Key (if using AI features)

---

## EC2 Instance Setup

### Step 1: Connect to EC2 Instance

From your local machine:

```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

Replace:
- `your-key.pem` with your EC2 key pair file
- `your-ec2-public-ip` with your EC2 instance public IP address

### Step 2: Update System Packages

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

---

## Transfer Project Files

### Option A: Using SCP (Recommended for First Deployment)

From your **local machine** (not on EC2):

```bash
# Navigate to project directory
cd /path/to/amu_pay13.1

# Transfer all files to EC2
scp -i your-key.pem -r * ubuntu@your-ec2-ip:/home/ubuntu/amu_pay/
```

### Option B: Using Git (Recommended for Updates)

On your **EC2 instance**:

```bash
# Install Git if not installed
sudo apt-get install -y git

# Clone your repository
cd /home/ubuntu
git clone your-repository-url amu_pay
cd amu_pay
```

---

## Initial Server Setup

### Step 1: Run Automated Setup Script

On your EC2 instance:

```bash
cd /home/ubuntu/amu_pay
chmod +x setup.sh deploy.sh
./setup.sh
```

The setup script will:
- ✅ Install Python 3.11 and pip
- ✅ Install MySQL client libraries
- ✅ Install Nginx web server
- ✅ Create Python virtual environment
- ✅ Install all Python dependencies
- ✅ Create necessary directories
- ✅ Set up file permissions
- ✅ Configure Nginx
- ✅ Set up systemd service

**Note:** When prompted about installing MySQL Server locally, choose **"n"** since you're using RDS.

### Step 2: Verify Setup

```bash
# Check Python version
python3.11 --version

# Check virtual environment
ls -la /home/ubuntu/amu_pay/venv

# Check Nginx installation
nginx -v
```

---

## RDS Database Configuration

### Step 1: Configure RDS Security Group

1. Go to **AWS Console** → **RDS** → **Databases** → Select your database
2. Click on **Connectivity & security** tab
3. Click on the **Security Group** (e.g., `sg-0f68aef52f442fe5e`)
4. Click **Edit inbound rules**
5. Click **Add rule**:
   - **Type:** MySQL/Aurora
   - **Port:** 3306
   - **Source:** 
     - Option A: Select your EC2 Security Group (most secure)
     - Option B: Your EC2 Private IP (if in same VPC)
     - Option C: `0.0.0.0/0` (less secure, only if publicly accessible)
6. Click **Save rules**

### Step 2: Create Database and User in RDS

Connect to your RDS instance. You can use:

**Option A: From EC2 (if mysql-client installed)**

```bash
# Install MySQL client
sudo apt-get install -y mysql-client

# Connect to RDS
mysql -h amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com \
      -u admin \
      -p
```

**Option B: From AWS RDS Query Editor** (if enabled)

**Option C: Using MySQL Workbench or DBeaver**

Once connected, run these SQL commands:

```sql
-- Create database
CREATE DATABASE amu_pay_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create application user (replace 'your-strong-password' with actual password)
CREATE USER 'amu_pay_user'@'%' IDENTIFIED BY 'your-strong-password';

-- Grant privileges
GRANT ALL PRIVILEGES ON amu_pay_db.* TO 'amu_pay_user'@'%';

-- Flush privileges
FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES;
SELECT user, host FROM mysql.user WHERE user = 'amu_pay_user';
```

**Note:** If you prefer to use the RDS master username directly, you can skip user creation and use the master credentials in your `.env` file.

### Step 3: Test RDS Connection from EC2

```bash
# Test connection with MySQL client
mysql -h amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com \
      -u amu_pay_user \
      -p \
      amu_pay_db
```

If connection succeeds, type `exit` to leave.

---

## Application Configuration

### Step 1: Create Environment File

```bash
cd /home/ubuntu/amu_pay
cp env.example .env
nano .env
```

### Step 2: Configure Environment Variables

Edit the `.env` file with your actual values:

```env
# ============================================
# Django Settings
# ============================================
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-ec2-ip,ec2-xx-xx-xx-xx.compute-1.amazonaws.com,localhost,127.0.0.1

# ============================================
# Database Configuration (Amazon RDS MySQL)
# ============================================
DB_ENGINE=django.db.backends.mysql
DB_NAME=amu_pay_db
DB_USER=amu_pay_user
DB_PASSWORD=your-rds-password-here
DB_HOST=amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com
DB_PORT=3306
DB_USE_SSL=True
DB_SSL_CA=/etc/ssl/certs/ca-certificates.crt

# ============================================
# JWT Settings
# ============================================
JWT_ACCESS_TOKEN_LIFETIME_DAYS=7
JWT_REFRESH_TOKEN_LIFETIME_DAYS=30

# ============================================
# Email Configuration (Gmail SMTP)
# ============================================
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
EMAIL_USE_TLS=True
FEEDBACK_ADMIN_EMAIL=your-email@gmail.com

# ============================================
# Twilio Configuration
# ============================================
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_CONTENT_SID=your-whatsapp-content-sid
TWILIO_WHATSAPP_FROM_NUMBER=whatsapp:+1234567890

# ============================================
# AI Integration
# ============================================
PINECONE_API_KEY=your-pinecone-api-key
GEMINI_API_KEY=your-gemini-api-key
PINECONE_INDEX_NAME=amu-pay-docs

# ============================================
# Message Settings
# ============================================
MESSAGE_MAX_LENGTH=1000
MESSAGE_MAX_FILE_SIZE_MB=10
MESSAGE_RETENTION_DAYS=365
ENABLE_IN_APP_NOTIFICATIONS=True
```

### Step 3: Generate Django Secret Key

```bash
cd /home/ubuntu/amu_pay
source venv/bin/activate
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

Copy the output and paste it as `SECRET_KEY` in your `.env` file.

### Step 4: Update ALLOWED_HOSTS

Replace `your-domain.com` and `your-ec2-ip` in `ALLOWED_HOSTS` with:
- Your actual domain name (if you have one)
- Your EC2 public IP address
- Your EC2 public DNS (e.g., `ec2-xx-xx-xx-xx.compute-1.amazonaws.com`)

Example:
```env
ALLOWED_HOSTS=amupay.com,54.123.45.67,ec2-54-123-45-67.eu-north-1.compute.amazonaws.com,localhost,127.0.0.1
```

### Step 5: Test Database Connection

```bash
cd /home/ubuntu/amu_pay
source venv/bin/activate
python test_rds_connection.py
```

Expected output:
```
============================================================
Testing RDS MySQL Connection
============================================================

Database Configuration:
  Engine: django.db.backends.mysql
  Host: amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com
  Port: 3306
  Database: amu_pay_db
  User: amu_pay_user
  SSL: {'ca': '/etc/ssl/certs/ca-certificates.crt'}

Attempting to connect...
✓ Connection successful!
  MySQL Version: 8.0.xx
  Current Database: amu_pay_db
  Tables found: 0
  Read/Write access: ✓

============================================================
Connection test PASSED!
============================================================
```

If you see errors, check the [Troubleshooting](#troubleshooting) section.

---

## Deploy Application

### Step 1: Run Database Migrations

```bash
cd /home/ubuntu/amu_pay
source venv/bin/activate

# Run migrations
python manage.py migrate

# If you see any migration warnings, you can ignore them for now
```

### Step 2: Create Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Enter:
- Username (e.g., `admin`)
- Email address
- Password (make it strong!)

### Step 3: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

This will create the `staticfiles` directory with all static assets.

### Step 4: Verify Application Structure

```bash
# Check directories exist
ls -la /home/ubuntu/amu_pay/
# Should see: staticfiles/, media/, venv/, manage.py, etc.

# Check permissions
ls -ld /home/ubuntu/amu_pay/staticfiles
ls -ld /home/ubuntu/amu_pay/media
```

### Step 5: Start Application Service

```bash
# Start the service
sudo systemctl start amu_pay

# Enable service to start on boot
sudo systemctl enable amu_pay

# Check status
sudo systemctl status amu_pay
```

Expected output should show `Active: active (running)`.

### Step 6: Check Application Logs

```bash
# View recent logs
sudo journalctl -u amu_pay -n 50

# Follow logs in real-time
sudo journalctl -u amu_pay -f
```

Look for any errors. If you see database connection errors, check your `.env` file and RDS security group.

---

## Configure Web Server

### Step 1: Update Nginx Configuration

The `nginx.conf` file should already be in your project. Verify it exists:

```bash
ls -la /home/ubuntu/amu_pay/nginx.conf
```

If needed, update the server name in `nginx.conf`:

```bash
nano /home/ubuntu/amu_pay/nginx.conf
```

Change:
```nginx
server_name _;  # Replace with your domain name or EC2 public IP
```

To:
```nginx
server_name your-domain.com your-ec2-ip;
```

### Step 2: Install Nginx Configuration

```bash
# Copy configuration
sudo cp /home/ubuntu/amu_pay/nginx.conf /etc/nginx/sites-available/amu_pay

# Create symbolic link
sudo ln -sf /etc/nginx/sites-available/amu_pay /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t
```

Expected output:
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Step 3: Start Nginx

```bash
# Start Nginx
sudo systemctl start nginx

# Enable Nginx on boot
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

### Step 4: Configure Firewall

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# If firewall is not enabled, enable it
sudo ufw --force enable

# Check firewall status
sudo ufw status
```

---

## SSL Certificate Setup

### Step 1: Install Certbot

```bash
sudo apt-get install -y certbot python3-certbot-nginx
```

### Step 2: Obtain SSL Certificate

**If you have a domain name:**

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Follow the prompts:
- Enter your email address
- Agree to terms of service
- Choose whether to redirect HTTP to HTTPS (recommended: Yes)

**If you don't have a domain name:**

You can skip SSL for now, but it's **highly recommended** for production. You can set it up later when you have a domain.

### Step 3: Test Certificate Renewal

```bash
sudo certbot renew --dry-run
```

Certbot automatically renews certificates. This test verifies the renewal process works.

---

## Verification & Testing

### Step 1: Test Application Endpoints

**Health Check:**
```bash
curl http://localhost/health/
# Should return: healthy
```

**From your browser or using curl:**
```bash
# Test from local machine
curl http://your-ec2-ip/health/

# Test admin endpoint (should redirect to login)
curl -I http://your-ec2-ip/admin/
```

### Step 2: Test Static Files

Visit in browser:
```
http://your-ec2-ip/static/
```

You should see the static files directory listing (or a 404 if no static files, which is normal).

### Step 3: Test Admin Panel

1. Visit: `http://your-ec2-ip/admin/` (or `https://your-domain.com/admin/` if SSL is configured)
2. Login with your superuser credentials
3. Verify you can access the Django admin panel

### Step 4: Test API Endpoints

```bash
# Test token endpoint (should return error without credentials, which is expected)
curl -X POST http://your-ec2-ip/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

### Step 5: Check All Services Status

```bash
# Check Django application
sudo systemctl status amu_pay

# Check Nginx
sudo systemctl status nginx

# Check if ports are listening
sudo netstat -tulpn | grep -E ':(80|443|8000)'
```

---

## Troubleshooting

### Application Won't Start

**Check service status:**
```bash
sudo systemctl status amu_pay
```

**Check logs:**
```bash
sudo journalctl -u amu_pay -n 100 --no-pager
```

**Common issues:**
- **Database connection error:** Check `.env` file, RDS security group, and credentials
- **Port already in use:** Check if another process is using port 8000: `sudo lsof -i :8000`
- **Permission denied:** Check file permissions: `sudo chown -R ubuntu:ubuntu /home/ubuntu/amu_pay`

### Database Connection Issues

**Test connection manually:**
```bash
mysql -h amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com \
      -u amu_pay_user \
      -p \
      amu_pay_db
```

**Check RDS Security Group:**
- Ensure MySQL (3306) is allowed from EC2 Security Group

**Check .env file:**
```bash
# Verify .env file exists and has correct values
cat /home/ubuntu/amu_pay/.env | grep DB_
```

**Test with Django:**
```bash
cd /home/ubuntu/amu_pay
source venv/bin/activate
python test_rds_connection.py
```

### Static Files Not Loading

**Re-collect static files:**
```bash
cd /home/ubuntu/amu_pay
source venv/bin/activate
python manage.py collectstatic --noinput
```

**Check permissions:**
```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/amu_pay/staticfiles
sudo chmod -R 755 /home/ubuntu/amu_pay/staticfiles
```

**Check Nginx configuration:**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Nginx Errors

**Test configuration:**
```bash
sudo nginx -t
```

**Check error logs:**
```bash
sudo tail -f /var/log/nginx/error.log
```

**Common issues:**
- **502 Bad Gateway:** Django application not running or not listening on port 8000
- **403 Forbidden:** Check file permissions and Nginx user permissions
- **404 Not Found:** Check Nginx configuration paths

### SSL Certificate Issues

**Check certificate status:**
```bash
sudo certbot certificates
```

**Renew certificate manually:**
```bash
sudo certbot renew
```

**Check Nginx SSL configuration:**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Permission Issues

**Fix ownership:**
```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/amu_pay
```

**Fix permissions:**
```bash
chmod +x /home/ubuntu/amu_pay/setup.sh
chmod +x /home/ubuntu/amu_pay/deploy.sh
```

### View All Logs

```bash
# Application logs
sudo journalctl -u amu_pay -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# System logs
sudo dmesg | tail
```

---

## Maintenance & Updates

### Deploying Updates

Use the deployment script:

```bash
cd /home/ubuntu/amu_pay
./deploy.sh
```

Or manually:

```bash
cd /home/ubuntu/amu_pay
source venv/bin/activate

# Pull latest code (if using Git)
git pull origin main

# Install/update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart application
sudo systemctl restart amu_pay

# Reload Nginx
sudo systemctl reload nginx
```

### Database Backups

**Manual backup:**
```bash
mysqldump -h amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com \
          -u amu_pay_user \
          -p \
          amu_pay_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

**Restore from backup:**
```bash
mysql -h amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com \
      -u amu_pay_user \
      -p \
      amu_pay_db < backup_20240101_120000.sql
```

**Note:** RDS also provides automated backups. Check AWS Console → RDS → Your Database → Automated backups.

### Monitoring

**Check application status:**
```bash
sudo systemctl status amu_pay
```

**Monitor resource usage:**
```bash
# CPU and memory
htop

# Disk usage
df -h

# Network connections
sudo netstat -tulpn
```

**Set up CloudWatch (AWS):**
- Enable CloudWatch monitoring in EC2 instance settings
- Set up alarms for CPU, memory, and disk usage

### Security Updates

**Update system packages:**
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

**Update Python packages:**
```bash
cd /home/ubuntu/amu_pay
source venv/bin/activate
pip list --outdated
pip install --upgrade package-name
```

### Common Maintenance Tasks

**Restart services:**
```bash
# Restart Django application
sudo systemctl restart amu_pay

# Restart Nginx
sudo systemctl restart nginx

# Restart both
sudo systemctl restart amu_pay nginx
```

**Clear Django cache (if using):**
```bash
cd /home/ubuntu/amu_pay
source venv/bin/activate
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
>>> exit()
```

**Check disk space:**
```bash
df -h
du -sh /home/ubuntu/amu_pay/*
```

---

## Quick Reference

### Important Files

- **Environment variables:** `/home/ubuntu/amu_pay/.env`
- **Nginx config:** `/etc/nginx/sites-available/amu_pay`
- **Systemd service:** `/etc/systemd/system/amu_pay.service`
- **Application logs:** `sudo journalctl -u amu_pay`
- **Nginx logs:** `/var/log/nginx/`

### Important Commands

```bash
# Application
sudo systemctl start|stop|restart|status amu_pay
sudo journalctl -u amu_pay -f

# Nginx
sudo systemctl start|stop|restart|status nginx
sudo nginx -t
sudo systemctl reload nginx

# Database
python test_rds_connection.py
python manage.py dbshell

# Django
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
```

### Your RDS Details

- **Endpoint:** `amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com`
- **Port:** `3306`
- **Region:** `eu-north-1`
- **Security Group:** `sg-0f68aef52f442fe5e`

### Support & Resources

- **Django Documentation:** https://docs.djangoproject.com/
- **AWS RDS Documentation:** https://docs.aws.amazon.com/rds/
- **Nginx Documentation:** https://nginx.org/en/docs/
- **Gunicorn Documentation:** https://docs.gunicorn.org/

---

## Security Checklist

Before going to production, ensure:

- [ ] `DEBUG=False` in `.env`
- [ ] Strong `SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` includes only your domain/IP
- [ ] SSL certificate installed (HTTPS)
- [ ] RDS Security Group restricts access
- [ ] Strong database passwords
- [ ] Firewall (UFW) configured
- [ ] Regular backups configured
- [ ] Monitoring enabled
- [ ] `.env` file not committed to Git
- [ ] Application user has minimal privileges

---

## Conclusion

Your AMU Pay application should now be fully deployed and running on EC2 with RDS MySQL!

**Next Steps:**
1. Test all API endpoints
2. Set up monitoring and alerts
3. Configure automated backups
4. Set up CI/CD pipeline (optional)
5. Review and optimize performance

**Need Help?**
- Check logs: `sudo journalctl -u amu_pay -f`
- Review this guide's troubleshooting section
- Check AWS CloudWatch for infrastructure issues

---

**Last Updated:** 2024
**Version:** 1.0

