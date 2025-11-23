# 🚀 How to Push Code Changes to AWS Server

There are several ways to deploy your code changes to AWS. Choose the method that works best for you.

## Method 1: Using SCP (Secure Copy) - Recommended for Quick Updates

This method copies files directly from your local machine to the AWS server.

### Step 1: Copy files to server
```bash
# From your local machine (Windows PowerShell or Git Bash)
# Replace with your actual server details:
# - your-key.pem: Your AWS EC2 key pair file
# - ubuntu@your-server-ip: Your server username and IP/domain

# Copy the entire project (if first time)
scp -i your-key.pem -r "amu_pay" ubuntu@your-server-ip:/home/ubuntu/amupay/

# OR copy just the changed files
scp -i your-key.pem "amu_pay/amu_pay/settings.py" ubuntu@your-server-ip:/home/ubuntu/amupay/amu_pay/amu_pay/
scp -i your-key.pem "test_db_connection.py" ubuntu@your-server-ip:/home/ubuntu/amupay/
```

### Step 2: SSH into server and deploy
```bash
# SSH into your server
ssh -i your-key.pem ubuntu@your-server-ip

# Navigate to project directory
cd /home/ubuntu/amupay/amu_pay

# Run deployment script
chmod +x ../../deploy.sh
../../deploy.sh
```

## Method 2: Using Git (If you have a Git repository)

This is the best method if your code is in a Git repository (GitHub, GitLab, etc.).

### Step 1: Push code to Git repository
```bash
# On your local machine
git add .
git commit -m "Fix SSL configuration for AWS RDS"
git push origin main  # or your branch name
```

### Step 2: Pull on server
```bash
# SSH into your server
ssh -i your-key.pem ubuntu@your-server-ip

# Navigate to project directory
cd /home/ubuntu/amupay/amu_pay

# Pull latest code
git pull origin main

# Run deployment script
../../deploy.sh
```

## Method 3: Manual File Transfer (Using WinSCP or FileZilla)

### Using WinSCP (Windows):
1. Download WinSCP: https://winscp.net/
2. Connect to your server:
   - Host: your-server-ip
   - Username: ubuntu
   - Private key: Select your .pem file
3. Navigate to `/home/ubuntu/amupay/amu_pay/amu_pay/`
4. Upload `settings.py` and `test_db_connection.py`
5. SSH into server and run `../../deploy.sh`

### Using FileZilla:
1. Download FileZilla: https://filezilla-project.org/
2. Use SFTP protocol
3. Connect with your .pem key file
4. Upload files same as WinSCP

## Method 4: Direct Edit on Server (For Quick Fixes)

For small changes, you can edit directly on the server:

```bash
# SSH into server
ssh -i your-key.pem ubuntu@your-server-ip

# Edit the file
cd /home/ubuntu/amupay/amu_pay/amu_pay
nano settings.py  # or use vim

# After editing, restart the service
sudo systemctl restart amu_pay
```

## Quick Deployment Commands (After Files are on Server)

Once your files are on the server, run these commands:

```bash
# SSH into server
ssh -i your-key.pem ubuntu@your-server-ip

# Navigate to project
cd /home/ubuntu/amupay/amu_pay

# Activate virtual environment
source amu_pay_env/bin/activate  # or venv/bin/activate

# Navigate to Django project
cd amu_pay

# Run migrations (if database changes)
python manage.py migrate --noinput

# Collect static files (if static files changed)
python manage.py collectstatic --noinput

# Restart the application
sudo systemctl restart amu_pay

# Check if it's running
sudo systemctl status amu_pay
```

## For Your Current Changes (SSL Fix)

Since you just updated `settings.py` and added `test_db_connection.py`, here's what to do:

### Option A: Quick SCP Method
```powershell
# In PowerShell on Windows (from your project directory)
scp -i "path\to\your-key.pem" "amu_pay\amu_pay\settings.py" ubuntu@your-server-ip:/home/ubuntu/amupay/amu_pay/amu_pay/
scp -i "path\to\your-key.pem" "test_db_connection.py" ubuntu@your-server-ip:/home/ubuntu/amupay/
```

Then SSH and run:
```bash
ssh -i your-key.pem ubuntu@your-server-ip
cd /home/ubuntu/amupay/amu_pay
source ../amu_pay_env/bin/activate
sudo systemctl restart amu_pay
```

### Option B: Use the Deploy Script
```bash
# After copying files, SSH and run:
ssh -i your-key.pem ubuntu@your-server-ip
cd /home/ubuntu/amupay
chmod +x deploy.sh
./deploy.sh
```

## Important Notes

1. **Backup First**: Always backup your `.env` file before deploying:
   ```bash
   cp /home/ubuntu/amupay/amu_pay/amu_pay/.env /home/ubuntu/amupay/amu_pay/amu_pay/.env.backup
   ```

2. **Check Service Status**: After deployment, always check:
   ```bash
   sudo systemctl status amu_pay
   sudo journalctl -u amu_pay -n 50  # View recent logs
   ```

3. **Test Database Connection**: After deploying the SSL fix:
   ```bash
   cd /home/ubuntu/amupay/amu_pay
   source ../amu_pay_env/bin/activate
   python test_db_connection.py
   python manage.py migrate
   ```

4. **Don't Overwrite .env**: Make sure your `.env` file on the server is not overwritten during deployment.

## Troubleshooting

### If files don't copy:
- Check your key file permissions: `chmod 400 your-key.pem`
- Verify server IP/domain is correct
- Ensure security group allows SSH (port 22)

### If deployment fails:
- Check logs: `sudo journalctl -u amu_pay -n 100`
- Verify virtual environment is activated
- Check file permissions: `ls -la /home/ubuntu/amupay/amu_pay/amu_pay/`

### If service won't restart:
- Check syntax errors: `python manage.py check`
- Verify database connection: `python manage.py dbshell`
- Check Nginx: `sudo nginx -t`

