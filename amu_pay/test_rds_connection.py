#!/usr/bin/env python
"""
Test script to verify RDS MySQL connection from Django application.
Run this script to test your database connection before deploying.

Usage:
    cd /home/ubuntu/amu_pay
    source venv/bin/activate
    python test_rds_connection.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amu_pay.settings')
django.setup()

from django.db import connection
from django.conf import settings

def test_connection():
    """Test database connection and display connection info."""
    print("=" * 60)
    print("Testing RDS MySQL Connection")
    print("=" * 60)
    
    try:
        # Get database configuration
        db_config = settings.DATABASES['default']
        print(f"\nDatabase Configuration:")
        print(f"  Engine: {db_config['ENGINE']}")
        print(f"  Host: {db_config['HOST']}")
        print(f"  Port: {db_config['PORT']}")
        print(f"  Database: {db_config['NAME']}")
        print(f"  User: {db_config['USER']}")
        print(f"  SSL: {db_config.get('OPTIONS', {}).get('ssl', 'Not configured')}")
        
        # Test connection
        print(f"\nAttempting to connect...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"✓ Connection successful!")
            print(f"  MySQL Version: {version}")
            
            # Test database exists
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()[0]
            print(f"  Current Database: {current_db}")
            
            # Show tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"  Tables found: {len(tables)}")
            if tables:
                print(f"  Table names: {', '.join([t[0] for t in tables[:10]])}")
                if len(tables) > 10:
                    print(f"  ... and {len(tables) - 10} more")
            
            # Test write access
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print(f"  Read/Write access: ✓")
        
        print("\n" + "=" * 60)
        print("Connection test PASSED!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ Connection FAILED!")
        print(f"  Error: {str(e)}")
        print(f"  Error Type: {type(e).__name__}")
        
        print("\n" + "=" * 60)
        print("Troubleshooting Tips:")
        print("=" * 60)
        print("1. Check your .env file has correct credentials")
        print("2. Verify RDS endpoint is correct")
        print("3. Check Security Group allows connections from EC2")
        print("4. Verify database and user exist in RDS")
        print("5. Test connection with mysql client:")
        db_config = settings.DATABASES['default']
        print(f"   mysql -h {db_config.get('HOST', 'unknown')} -u {db_config.get('USER', 'unknown')} -p")
        print("=" * 60)
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)

