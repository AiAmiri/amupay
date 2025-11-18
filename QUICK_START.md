# Quick Start Guide - EC2 Deployment

## Prerequisites Checklist

- [ ] EC2 instance running Ubuntu 22.04 LTS
- [ ] Security Group allows ports: 22, 80, 443, 8000
- [ ] SSH key pair for EC2 access
- [ ] Database credentials (RDS or local MySQL)
- [ ] All API keys (Twilio, Pinecone, Gemini)
- [ ] Email credentials (Gmail app password)

## Quick Deployment Steps

### 1. Connect to EC2

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 2. Transfer Project Files

```bash
# From your local machine
scp -i your-key.pem -r amu_pay13.1/* ubuntu@your-ec2-ip:/home/ubuntu/amu_pay/
```

### 3. Run Setup

```bash
cd /home/ubuntu/amu_pay
chmod +x setup.sh deploy.sh
./setup.sh
```

### 4. Configure Environment

```bash
nano .env
# Fill in all required values from env.example
```

### 5. Setup Database

**For RDS (Your setup):**
- Update `.env` with RDS credentials:
  ```env
  DB_HOST=amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com
  DB_PORT=3306
  DB_NAME=amu_pay_db
  DB_USER=your-rds-username
  DB_PASSWORD=your-rds-password
  DB_USE_SSL=True
  ```
- Configure RDS Security Group (see RDS_SETUP.md)
- Create database in RDS
- Test connection: `python test_rds_connection.py`

**For Local MySQL:**
```bash
sudo mysql -u root -p
CREATE DATABASE amu_pay_db;
CREATE USER 'amu_pay_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON amu_pay_db.* TO 'amu_pay_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 6. Initialize Application

```bash
cd /home/ubuntu/amu_pay
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 7. Start Services

```bash
sudo systemctl start amu_pay
sudo systemctl enable amu_pay
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 8. Verify

Visit: `http://your-ec2-ip` or `http://your-domain.com`

## Common Commands

```bash
# Check application status
sudo systemctl status amu_pay

# View application logs
sudo journalctl -u amu_pay -f

# Restart application
sudo systemctl restart amu_pay

# Deploy updates
./deploy.sh

# Check Nginx status
sudo systemctl status nginx

# Test Nginx config
sudo nginx -t
```

## Troubleshooting

**Application won't start:**
```bash
sudo journalctl -u amu_pay -n 50
```

**Database connection error:**
- Check `.env` file has correct DB credentials
- Verify MySQL is running: `sudo systemctl status mysql`
- Test connection: `mysql -h $DB_HOST -u $DB_USER -p`

**Static files 404:**
```bash
python manage.py collectstatic --noinput
sudo chown -R ubuntu:ubuntu staticfiles
```

## Next Steps

1. Set up SSL certificate (Let's Encrypt)
2. Configure domain name DNS
3. Set up automated backups
4. Configure monitoring
5. Review security settings

For detailed instructions, see `DEPLOYMENT.md`

