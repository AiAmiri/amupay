#!/usr/bin/env python3
"""
Script to create .env file for AMU Pay project
Run this script to create a .env file with your current configuration
"""

import os

# Environment variables template
ENV_CONTENT = """# Django Configuration
DEBUG=True
SECRET_KEY=django-insecure-6ddu577z-%4tik1)%h(8=y-cm!hcmu4s$4qm+q(u35s4m-5h_8
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,*

# Database Configuration
DB_ENGINE=django.db.backends.mysql
DB_NAME=amu_pay_db
DB_USER=root
DB_PASSWORD=amiriroot
DB_HOST=localhost
DB_PORT=3306

# JWT Configuration
JWT_ACCESS_TOKEN_LIFETIME_DAYS=7
JWT_REFRESH_TOKEN_LIFETIME_DAYS=1

# Email Configuration (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=ali.amiri.cursor@gmail.com
EMAIL_HOST_PASSWORD=aagk rdwx wvhc tsbz
EMAIL_USE_TLS=True

# Twilio Configuration
TWILIO_ACCOUNT_SID=AC59d45f9dd4ee0851f9adb299d742b18e
TWILIO_AUTH_TOKEN=b7beecbdbade842ffc9afb9ec57dab19
TWILIO_PHONE_NUMBER=+16693304013
TWILIO_WHATSAPP_CONTENT_SID=HX229f5a04fd0510ce1b071852155d3e75
TWILIO_WHATSAPP_FROM_NUMBER=+14155238886

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOW_CREDENTIALS=True

# Message Settings
MESSAGE_MAX_LENGTH=1000
MESSAGE_MAX_FILE_SIZE_MB=10
MESSAGE_RETENTION_DAYS=365
ENABLE_IN_APP_NOTIFICATIONS=True

# Security Settings
USE_HTTPS=False
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Static Files
STATIC_URL=/static/
MEDIA_URL=/media/

# Logging Level
LOG_LEVEL=INFO

# Time Zone
TIME_ZONE=UTC
LANGUAGE_CODE=en-us
USE_I18N=True
USE_TZ=True
"""

def create_env_file():
    """Create .env file in the current directory"""
    env_path = '.env'
    
    if os.path.exists(env_path):
        response = input(f".env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled. .env file not modified.")
            return
    
    try:
        with open(env_path, 'w') as f:
            f.write(ENV_CONTENT.strip())
        
        print(f"✅ Successfully created .env file at: {os.path.abspath(env_path)}")
        print("\n📝 Next steps:")
        print("1. Review the .env file and update values as needed")
        print("2. Add .env to your .gitignore file")
        print("3. For production, use secure values for SECRET_KEY, passwords, etc.")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == "__main__":
    print("🔧 AMU Pay Environment Configuration Setup")
    print("=" * 50)
    create_env_file()
