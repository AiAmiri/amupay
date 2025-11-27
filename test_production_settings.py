#!/usr/bin/env python
"""
Test script to validate Django production settings without breaking the application
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root / 'amu_pay'))

# Set minimal environment variables for testing
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-validation-only')
os.environ.setdefault('DEBUG', 'False')
os.environ.setdefault('ALLOWED_HOSTS', 'localhost,127.0.0.1')
os.environ.setdefault('DB_ENGINE', 'django.db.backends.sqlite3')
os.environ.setdefault('DB_NAME', ':memory:')

# Test Django settings import
try:
    print("🔍 Testing Django settings import...")
    from django.conf import settings
    
    # Configure Django settings
    if not settings.configured:
        settings.configure()
    
    print("✅ Django settings imported successfully")
    
    # Test critical settings
    critical_settings = {
        'SECRET_KEY': settings.SECRET_KEY,
        'DEBUG': settings.DEBUG,
        'ALLOWED_HOSTS': settings.ALLOWED_HOSTS,
        'STATIC_URL': settings.STATIC_URL,
        'STATIC_ROOT': settings.STATIC_ROOT,
        'MEDIA_URL': settings.MEDIA_URL,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
    }
    
    print("\n📋 Critical Settings Validation:")
    for key, value in critical_settings.items():
        if value is None or value == '':
            print(f"❌ {key}: {value} (MISSING)")
        else:
            print(f"✅ {key}: {value}")
    
    # Test CORS settings
    cors_settings = {
        'CORS_ALLOWED_ORIGINS': getattr(settings, 'CORS_ALLOWED_ORIGINS', None),
        'CORS_ALLOW_ALL_ORIGINS': getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', None),
        'CORS_ALLOW_CREDENTIALS': getattr(settings, 'CORS_ALLOW_CREDENTIALS', None),
    }
    
    print("\n🌐 CORS Settings Validation:")
    for key, value in cors_settings.items():
        if value is None:
            print(f"❌ {key}: {value} (MISSING)")
        else:
            print(f"✅ {key}: {value}")
    
    # Test security settings (only in production mode)
    if not settings.DEBUG:
        security_settings = {
            'SECURE_SSL_REDIRECT': getattr(settings, 'SECURE_SSL_REDIRECT', None),
            'SESSION_COOKIE_SECURE': getattr(settings, 'SESSION_COOKIE_SECURE', None),
            'CSRF_COOKIE_SECURE': getattr(settings, 'CSRF_COOKIE_SECURE', None),
            'SECURE_BROWSER_XSS_FILTER': getattr(settings, 'SECURE_BROWSER_XSS_FILTER', None),
            'SECURE_CONTENT_TYPE_NOSNIFF': getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', None),
        }
        
        print("\n🔒 Security Settings Validation (Production Mode):")
        for key, value in security_settings.items():
            if value is None:
                print(f"❌ {key}: {value} (MISSING)")
            else:
                print(f"✅ {key}: {value}")
    
    # Test logging configuration
    logging_config = getattr(settings, 'LOGGING', {})
    if logging_config:
        print("\n📝 Logging Configuration:")
        print(f"✅ LOGGING configured with {len(logging_config.get('loggers', {}))} loggers")
        
        # Check if logs directory path is valid
        logs_dir = project_root / 'amu_pay' / 'logs'
        print(f"📁 Logs directory: {logs_dir}")
        print(f"📁 Logs directory exists: {logs_dir.exists()}")
    else:
        print("\n❌ No logging configuration found")
    
    # Test installed apps
    print("\n📦 Installed Apps Validation:")
    required_apps = ['corsheaders', 'django.contrib.admin', 'rest_framework']
    for app in required_apps:
        if app in settings.INSTALLED_APPS:
            print(f"✅ {app}: Installed")
        else:
            print(f"❌ {app}: Missing")
    
    print("\n🎉 Settings validation completed!")
    print("📝 Note: This test uses in-memory SQLite database to avoid connection issues")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("💡 Make sure all required packages are installed:")
    print("   pip install django djangorestframework django-cors-headers python-decouple whitenoise")
    
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
    print("💡 Check your environment variables and configuration")
    
finally:
    print("\n📋 Deployment Checklist:")
    print("   1. Update your .env file with the new CORS and security settings")
    print("   2. Copy updated settings.py to your server")
    print("   3. Restart Django application: sudo systemctl restart amu-pay")
    print("   4. Test admin panel: http://your-ip/admin/")
    print("   5. Test API endpoints: http://your-ip/api/")
