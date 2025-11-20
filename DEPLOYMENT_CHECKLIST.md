# 🚀 AWS Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. Environment Configuration
- [ ] Copy `env.example` to `.env` on EC2
- [ ] Set `SECRET_KEY` (generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure `ALLOWED_HOSTS` with your EC2 domain/IP
- [ ] Set all database credentials (DB_USER, DB_PASSWORD, DB_HOST)
- [ ] Configure email settings (EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
- [ ] Configure Twilio credentials
- [ ] Set AI API keys (PINECONE_API_KEY, GEMINI_API_KEY)

### 2. AWS RDS Setup
- [ ] RDS instance is running and accessible
- [ ] Security Group allows connections from EC2 Security Group on port 3306
- [ ] Database `amu_pay_db` exists in RDS
- [ ] Database user has proper permissions
- [ ] SSL connection configured (if using DB_USE_SSL=True)

### 3. EC2 Instance Setup
- [ ] EC2 instance is running (Ubuntu 22.04 LTS recommended)
- [ ] Security Group allows HTTP (80) and HTTPS (443) from internet
- [ ] SSH access configured
- [ ] Python 3.11+ installed
- [ ] MySQL client libraries installed

### 4. Code Deployment
- [ ] Code is pushed to repository or uploaded to EC2
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with production values

## 📋 Deployment Steps

### Step 1: Initial Server Setup
```bash
# Run setup script
chmod +x setup.sh
./setup.sh
```

### Step 2: Configure Environment
```bash
cd /home/ubuntu/amu_pay/amu_pay
cp ../../env.example .env
nano .env  # Edit with your production values
```

### Step 3: Database Migration
```bash
source ../venv/bin/activate
python manage.py migrate --noinput
```

### Step 4: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 5: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 6: Setup Systemd Service
```bash
sudo cp ../../amu_pay.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable amu_pay
sudo systemctl start amu_pay
sudo systemctl status amu_pay
```

### Step 7: Setup Nginx
```bash
sudo cp ../../nginx.conf /etc/nginx/sites-available/amu_pay
sudo ln -s /etc/nginx/sites-available/amu_pay /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

### Step 8: Verify Deployment
```bash
# Check service status
sudo systemctl status amu_pay
sudo systemctl status nginx

# Check logs
sudo journalctl -u amu_pay -f
sudo tail -f /var/log/nginx/error.log

# Test health endpoint
curl http://localhost/health/
```

## 🔧 Post-Deployment

### Verify Application
- [ ] Application responds on HTTP (port 80)
- [ ] Admin panel accessible at `/admin/`
- [ ] API endpoints responding
- [ ] Static files loading correctly
- [ ] Media files accessible
- [ ] Database connections working

### Security Hardening
- [ ] SSL certificate installed (Let's Encrypt recommended)
- [ ] HTTPS redirect enabled in settings
- [ ] Firewall configured (UFW)
- [ ] Regular backups configured
- [ ] Log rotation configured

### Monitoring
- [ ] Set up CloudWatch logs (optional)
- [ ] Configure error alerting
- [ ] Monitor database performance
- [ ] Set up automated backups

## 🐛 Troubleshooting

### Service Not Starting
```bash
# Check service logs
sudo journalctl -u amu_pay -n 50

# Check for errors
python manage.py check --deploy
```

### Database Connection Issues
- Verify RDS Security Group rules
- Check `.env` database credentials
- Test connection: `mysql -h <RDS_HOST> -u <USER> -p`

### Static Files Not Loading
```bash
# Recollect static files
python manage.py collectstatic --noinput --clear

# Check permissions
sudo chown -R ubuntu:ubuntu staticfiles/
```

### Nginx Errors
```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log
```

## 📝 Quick Commands

### Restart Application
```bash
sudo systemctl restart amu_pay
```

### View Logs
```bash
sudo journalctl -u amu_pay -f
```

### Update Code
```bash
cd /home/ubuntu/amu_pay/amu_pay
git pull  # or upload new code
source ../venv/bin/activate
pip install -r ../requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
sudo systemctl restart amu_pay
```

### Backup Database
```bash
mysqldump -h <RDS_HOST> -u <USER> -p amu_pay_db > backup_$(date +%Y%m%d).sql
```

## 🔐 Security Notes

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Use strong SECRET_KEY** - Generate unique key for production
3. **Keep DEBUG=False** - Prevents information leakage
4. **Configure ALLOWED_HOSTS** - Restrict to your domain/IP
5. **Enable SSL/HTTPS** - Encrypt traffic in production
6. **Regular updates** - Keep dependencies and system updated

## 📞 Support

For issues, check:
- Django logs: `sudo journalctl -u amu_pay`
- Nginx logs: `/var/log/nginx/error.log`
- Application logs: Check Django settings for logging configuration

