# 🌐 How to Access Your AWS Project

There are two scenarios: accessing the deployed app on AWS, or running it locally.

## Scenario 1: Accessing the Application on AWS Server

### Step 1: Get Your EC2 Public IP or Domain

1. **From AWS Console:**
   - Go to EC2 Dashboard
   - Click on "Instances"
   - Find your instance
   - Copy the "Public IPv4 address" or "Public IPv4 DNS"

2. **Or from your server (SSH):**
   ```bash
   curl http://169.254.169.254/latest/meta-data/public-ipv4
   ```

### Step 2: Check if Services are Running

SSH into your server and check:

```bash
# Check if Gunicorn (Django app) is running
sudo systemctl status amu_pay

# Check if Nginx is running
sudo systemctl status nginx

# Check if port 80 is listening
sudo netstat -tlnp | grep :80
```

### Step 3: Access in Browser

Open your web browser and go to:

```
http://your-ec2-public-ip
```

**Example:**
```
http://54.123.45.67
```

Or if you have a domain configured:
```
http://yourdomain.com
```

### Step 4: Check Security Group

If you can't access it, make sure your EC2 Security Group allows:
- **Inbound Rule:** HTTP (port 80) from `0.0.0.0/0` (or your IP)
- **Inbound Rule:** HTTPS (port 443) if using SSL

**To check/fix:**
1. Go to EC2 → Security Groups
2. Select your instance's security group
3. Edit Inbound Rules
4. Add rule: Type=HTTP, Port=80, Source=0.0.0.0/0

### Step 5: Test Endpoints

```bash
# Health check (from server)
curl http://localhost/health/

# Or from your local machine
curl http://your-ec2-public-ip/health/
```

## Scenario 2: Running the Project Locally on Your Machine

If you want to run the project on your local Windows machine:

### Step 1: Setup Local Environment

```powershell
# Navigate to project directory
cd "C:\Users\Dell.com\Desktop\deploy finali\amu_pay13.1\amu_pay"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Local .env File

Create a `.env` file in `amu_pay/amu_pay/` directory:

```env
# For local development, you can use SQLite or connect to RDS
SECRET_KEY=your-local-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Option A: Use SQLite (easiest for local)
# (No DB settings needed, Django will use SQLite by default)

# Option B: Connect to AWS RDS (same as production)
DB_ENGINE=django.db.backends.mysql
DB_NAME=amu_pay_db
DB_USER=your-rds-username
DB_PASSWORD=your-rds-password
DB_HOST=amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com
DB_PORT=3306
DB_USE_SSL=True
DB_SSL_CA=  # Leave empty or download RDS CA bundle
```

### Step 3: Run Migrations

```powershell
python manage.py migrate
```

### Step 4: Create Superuser (Optional)

```powershell
python manage.py createsuperuser
```

### Step 5: Run Development Server

```powershell
python manage.py runserver
```

### Step 6: Access Locally

Open your browser and go to:
```
http://127.0.0.1:8000
```
or
```
http://localhost:8000
```

## Troubleshooting

### Can't Access AWS Server

**Problem:** Browser shows "This site can't be reached"

**Solutions:**
1. Check Security Group allows port 80
2. Check if services are running:
   ```bash
   sudo systemctl status amu_pay
   sudo systemctl status nginx
   ```
3. Check firewall on server:
   ```bash
   sudo ufw status
   sudo ufw allow 80/tcp
   ```
4. Check Nginx configuration:
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Services Not Running

**Start services:**
```bash
# Start Django app
sudo systemctl start amu_pay

# Start Nginx
sudo systemctl start nginx

# Enable to start on boot
sudo systemctl enable amu_pay
sudo systemctl enable nginx
```

### Check Logs

```bash
# Django/Gunicorn logs
sudo journalctl -u amu_pay -f

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Nginx access logs
sudo tail -f /var/log/nginx/access.log
```

### Test Connection from Server

```bash
# Test if app responds locally
curl http://localhost:8000

# Test if Nginx responds
curl http://localhost

# Test health endpoint
curl http://localhost/health/
```

## Quick Access Commands

### On AWS Server:
```bash
# Get public IP
curl http://169.254.169.254/latest/meta-data/public-ipv4

# Check if app is accessible
curl http://localhost/health/

# View real-time logs
sudo journalctl -u amu_pay -f
```

### From Your Local Machine:
```powershell
# Test if server is reachable
ping your-ec2-public-ip

# Test HTTP connection
curl http://your-ec2-public-ip/health/
```

## Common URLs

Once accessible, you can visit:
- **Home/API:** `http://your-ec2-ip/`
- **Admin Panel:** `http://your-ec2-ip/admin/`
- **Health Check:** `http://your-ec2-ip/health/`
- **API Endpoints:** `http://your-ec2-ip/api/...` (depends on your URL configuration)

## Next Steps

1. **Set up a domain name** (optional):
   - Point your domain to EC2 IP
   - Update `ALLOWED_HOSTS` in `.env`
   - Configure Nginx with domain name

2. **Enable HTTPS** (recommended):
   - Install Let's Encrypt SSL certificate
   - Update Nginx configuration for HTTPS
   - Set `SECURE_SSL_REDIRECT=True` in settings

3. **Monitor the application:**
   - Set up CloudWatch logs
   - Monitor server resources
   - Set up alerts


p,