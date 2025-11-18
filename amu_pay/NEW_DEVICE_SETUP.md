# New Device Setup Guide - AMU_Pay

This guide will help you set up the AMU_Pay project on a new device without migration errors.

## Quick Setup (Recommended)

### Option 1: Fresh Installation (No existing database)

If you're starting fresh on a new device:

```bash
# 1. Clone or copy the project
cd amu_pay13/amu_pay

# 2. Create virtual environment (if not already created)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment variables
# Copy your .env file or create a new one from .env.example
# Required variables:
# - SECRET_KEY
# - DB_NAME
# - DB_USER
# - DB_PASSWORD
# - DB_HOST
# - DB_PORT
# - EMAIL_HOST_USER
# - EMAIL_HOST_PASSWORD
# - TWILIO_ACCOUNT_SID
# - TWILIO_AUTH_TOKEN
# - TWILIO_PHONE_NUMBER

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. (Optional) Load initial data
python manage.py loaddata initial_data

# 8. Run the server
python manage.py runserver
```

### Option 2: Reset Existing Migrations

If you have conflicts or issues with existing migrations:

**For Windows:**
```bash
python reset_migrations.py
```

**For Linux/Mac:**
```bash
chmod +x reset_migrations.sh
./reset_migrations.sh
```

### Option 3: Manual Migration Reset

If you prefer manual control:

```bash
# 1. Delete all migration files (keep __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
# Windows PowerShell:
# Get-ChildItem -Path . -Filter "*.py" -Recurse | Where-Object { $_.DirectoryName -like "*migrations*" -and $_.Name -ne "__init__.py" } | Remove-Item

# 2. Delete database
rm db.sqlite3
# Windows:
# del db.sqlite3

# 3. Recreate migrations
python manage.py makemigrations

# 4. Apply migrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser
```

## Common Migration Errors & Solutions

### Error 1: "No migrations to apply"
**Solution:**
```bash
# Check migration status
python manage.py showmigrations

# Fake migrations if needed
python manage.py migrate --fake

# Or reset completely using Option 2 above
```

### Error 2: "InconsistentMigrationHistory"
**Solution:**
```bash
# Check which migrations are causing issues
python manage.py showmigrations

# Mark specific migration as fake if already applied in database
python manage.py migrate app_name 0002_migration_name --fake

# Or reset completely using Option 2
```

### Error 3: "Table already exists"
**Solution:**
```bash
# Check what's in the database
python manage.py dbshell

# Fake initial migration if tables already exist
python manage.py migrate app_name 0001_initial --fake

# Or reset completely using Option 2
```

### Error 4: "Module not found"
**Solution:**
```bash
# Make sure all apps are in INSTALLED_APPS in settings.py
# Check for duplicate migration folders
# Delete any empty migration folders outside amu_pay directory

# Clean Python cache
find . -type d -name __pycache__ -exec rm -r {} +
# Windows PowerShell:
# Get-ChildItem -Path . -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force

python manage.py makemigrations
python manage.py migrate
```

### Error 5: Foreign Key Constraint Errors
**Solution:**
```bash
# Make sure dependent migrations are run first
python manage.py migrate saraf_account
python manage.py migrate currency amber manage.py migrate hawala

# Or reset completely using Option 2
```

## Important Notes

1. **Never delete or modify migrations in production** without backing up the database first.

2. **The reset scripts are for development only**. Never run them on a production server.

3. **Always backup your database** before running migrations:
   ```bash
   python manage.py dumpdata > backup.json
   ```

4. **Migrations must be committed to version control**. Never edit existing migrations, only create new ones.

5. **Dependency order under amu_pay**: saraf_account → currency → hawala → others

## Migration Files Location

All migration files should be in:
```
amu_pay/
├── saraf_account/migrations/
├── currency/migrations/
├── hawala/migrations/
├── email_otp/migrations/
├── phone_otp/migrations/
├── wa_otp/migrations/
├── msg/migrations/
├── normal_user_account/migrations/
├── saraf_create_accounts/migrations/
├── exchange/migrations/
├── saraf_post/migrations/
├── saraf_social/migrations/
├── saraf_balance/migrations/
└── transaction/migrations/
```

**DO NOT** create migrations in root directories outside `amu_pay/`.

## Verification

After setup, verify everything works:

```bash
# 1. Check migration status
python manage.py showmigrations

# 2. Check for issues
python manage.py check

# 3. Test server
python manage.py runserver

# 4. Test database connection
python manage.py dbshell
```

## Need Help?

If you encounter errors not covered here:
1. Check the error message carefully
2. Run `python manage.py showmigrations` to see what's applied
3. Check Django migration docs: https://docs.djangoproject.com/en/stable/topics/migrations/
4. Use the migration reset script if in doubt (development only)

