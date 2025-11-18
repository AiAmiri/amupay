# Amazon RDS MySQL Setup Guide

This guide will help you connect your Django application to Amazon RDS MySQL database.

## RDS Database Information

Based on your RDS instance:
- **Endpoint:** `amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com`
- **Port:** `3306`
- **Region:** `eu-north-1`
- **Publicly Accessible:** Yes
- **Security Group:** `default (sg-0f68aef52f442fe5e)`

## Step 1: Configure Security Group

Your EC2 instance must be able to connect to RDS. Update the RDS security group to allow inbound connections from your EC2 instance:

1. Go to AWS Console → RDS → Your Database → Connectivity & Security
2. Click on the Security Group (e.g., `sg-0f68aef52f442fe5e`)
3. Add Inbound Rule:
   - **Type:** MySQL/Aurora (3306)
   - **Source:** 
     - Option A: Your EC2 Security Group (recommended)
     - Option B: Your EC2 Private IP (if in same VPC)
     - Option C: `0.0.0.0/0` (only if publicly accessible - less secure)

## Step 2: Create Database and User in RDS

Connect to your RDS instance and create the database:

```bash
# Connect to RDS from EC2 (if mysql-client is installed)
mysql -h amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com -u admin -p
```

Or use MySQL Workbench, DBeaver, or any MySQL client.

Once connected, run:

```sql
-- Create database
CREATE DATABASE amu_pay_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (replace 'your-password' with a strong password)
CREATE USER 'amu_pay_user'@'%' IDENTIFIED BY 'your-password';

-- Grant privileges
GRANT ALL PRIVILEGES ON amu_pay_db.* TO 'amu_pay_user'@'%';

-- Flush privileges
FLUSH PRIVILEGES;

-- Verify
SHOW DATABASES;
SELECT user, host FROM mysql.user;
```

**Note:** If your RDS instance uses a master username (like `admin`), you can either:
- Use the master username directly (not recommended for production)
- Create a new user as shown above (recommended)

## Step 3: Configure Environment Variables

Update your `.env` file on EC2:

```bash
cd /home/ubuntu/amu_pay
nano .env
```

Update these values:

```env
# Database Configuration (Amazon RDS MySQL)
DB_ENGINE=django.db.backends.mysql
DB_NAME=amu_pay_db
DB_USER=amu_pay_user
DB_PASSWORD=your-actual-password
DB_HOST=amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com
DB_PORT=3306

# SSL Configuration for RDS (recommended for security)
DB_USE_SSL=True
DB_SSL_CA=/etc/ssl/certs/ca-certificates.crt
```

## Step 4: Test Database Connection

From your EC2 instance, test the connection:

```bash
# Install MySQL client if not already installed
sudo apt-get install mysql-client

# Test connection
mysql -h amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com \
      -u amu_pay_user \
      -p \
      amu_pay_db
```

If connection succeeds, you're ready to proceed.

## Step 5: Run Django Migrations

```bash
cd /home/ubuntu/amu_pay
source venv/bin/activate

# Test database connection with Django
python manage.py check --database default

# Run migrations
python manage.py migrate

# Create superuser (if needed)
python manage.py createsuperuser
```

## Step 6: Verify Connection

Test the connection using the test script:

```bash
cd /home/ubuntu/amu_pay
source venv/bin/activate
python test_rds_connection.py
```

Or use Django's dbshell:

```bash
python manage.py dbshell
```

You should see the MySQL prompt. Type `exit` to leave.

## SSL Configuration (Optional but Recommended)

For secure connections, you can download the RDS CA certificate:

```bash
# Download RDS CA bundle
wget https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -O /home/ubuntu/rds-ca-bundle.pem

# Update .env
DB_SSL_CA=/home/ubuntu/rds-ca-bundle.pem
```

Then restart your application:

```bash
sudo systemctl restart amu_pay
```

## Troubleshooting

### Connection Refused

**Problem:** Can't connect to RDS from EC2

**Solutions:**
1. Check Security Group rules allow inbound MySQL (3306) from EC2
2. Verify RDS is publicly accessible (if connecting from outside VPC)
3. Check EC2 Security Group allows outbound traffic
4. Verify endpoint and port are correct

### Authentication Failed

**Problem:** `Access denied for user`

**Solutions:**
1. Verify username and password in `.env`
2. Check user exists in RDS: `SELECT user, host FROM mysql.user;`
3. Verify user has privileges: `SHOW GRANTS FOR 'amu_pay_user'@'%';`
4. Try connecting with master username first to verify RDS is accessible

### SSL Connection Error

**Problem:** SSL connection issues

**Solutions:**
1. Set `DB_USE_SSL=False` temporarily to test
2. Download RDS CA certificate bundle
3. Verify certificate path is correct
4. Check file permissions: `chmod 644 /path/to/certificate.pem`

### Database Does Not Exist

**Problem:** `Unknown database 'amu_pay_db'`

**Solutions:**
1. Connect to RDS and create database (see Step 2)
2. Verify database name in `.env` matches created database
3. Check user has privileges on the database

## Security Best Practices

1. **Use SSL:** Always enable SSL for RDS connections (`DB_USE_SSL=True`)
2. **Strong Passwords:** Use complex passwords for database users
3. **Least Privilege:** Grant only necessary privileges to application user
4. **Security Groups:** Restrict access to specific IPs or security groups
5. **Private Subnet:** Consider making RDS private (not publicly accessible) if EC2 is in same VPC
6. **Backup:** Enable automated backups in RDS
7. **Encryption:** Enable encryption at rest for RDS

## Connection String Format

For reference, your connection details:
```
Host: amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com
Port: 3306
Database: amu_pay_db
User: amu_pay_user
Password: [your-password]
SSL: Enabled (recommended)
```

## Next Steps

After successful connection:
1. Run migrations: `python manage.py migrate`
2. Create superuser: `python manage.py createsuperuser`
3. Load initial data (if any)
4. Test application endpoints
5. Set up automated backups
6. Monitor database performance

## Additional Resources

- [AWS RDS Documentation](https://docs.aws.amazon.com/rds/)
- [Django Database Configuration](https://docs.djangoproject.com/en/stable/ref/settings/#databases)
- [MySQL SSL Configuration](https://dev.mysql.com/doc/refman/8.0/en/using-encrypted-connections.html)

