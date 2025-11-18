# RDS Connection Quick Reference

## Your RDS Details
- **Endpoint:** `amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com`
- **Port:** `3306`
- **Region:** `eu-north-1`
- **Security Group:** `sg-0f68aef52f442fe5e`

## Quick Setup Steps

### 1. Update .env file
```env
DB_HOST=amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com
DB_PORT=3306
DB_NAME=amu_pay_db
DB_USER=your-rds-username
DB_PASSWORD=your-rds-password
DB_USE_SSL=True
```

### 2. Configure Security Group
- AWS Console → RDS → Your DB → Security Group
- Add Inbound Rule: MySQL (3306) from your EC2 Security Group

### 3. Create Database in RDS
```sql
CREATE DATABASE amu_pay_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'amu_pay_user'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON amu_pay_db.* TO 'amu_pay_user'@'%';
FLUSH PRIVILEGES;
```

### 4. Test Connection
```bash
cd /home/ubuntu/amu_pay
source venv/bin/activate
python test_rds_connection.py
```

### 5. Run Migrations
```bash
python manage.py migrate
python manage.py createsuperuser
```

## Connection Test Commands

**Using MySQL client:**
```bash
mysql -h amupaydb.cxea220s03us.eu-north-1.rds.amazonaws.com -u username -p
```

**Using Django:**
```bash
python manage.py dbshell
python test_rds_connection.py
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Connection refused | Check Security Group allows port 3306 from EC2 |
| Access denied | Verify username/password in .env |
| Database doesn't exist | Create database in RDS (see Step 3) |
| SSL error | Set `DB_USE_SSL=False` to test, then fix SSL config |

## Full Documentation
See `RDS_SETUP.md` for complete setup instructions.

