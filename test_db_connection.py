#!/usr/bin/env python
"""
Diagnostic script to test database connection and identify SSL issues.
Run this on your AWS server to diagnose the problem.

Usage:
    python test_db_connection.py
"""

import os
import sys
from decouple import config

def test_ssl_certificate_exists():
    """Check if SSL certificate files exist"""
    print("=" * 60)
    print("1. Checking SSL Certificate Files")
    print("=" * 60)
    
    ca_paths = [
        config('DB_SSL_CA', default=None),
        '/etc/ssl/certs/ca-certificates.crt',
        '/home/ubuntu/rds-ca-bundle.pem',
    ]
    
    found = False
    for path in ca_paths:
        if path and os.path.exists(path):
            print(f"✓ Found: {path}")
            found = True
        elif path:
            print(f"✗ Missing: {path}")
    
    if not found:
        print("\n⚠️  No SSL certificate files found!")
        print("   This is likely the problem if DB_USE_SSL=True")
    
    return found

def check_env_config():
    """Check .env configuration"""
    print("\n" + "=" * 60)
    print("2. Checking .env Configuration")
    print("=" * 60)
    
    db_use_ssl = config('DB_USE_SSL', default=False, cast=bool)
    db_ssl_ca = config('DB_SSL_CA', default=None)
    db_host = config('DB_HOST', default='localhost')
    
    print(f"DB_USE_SSL = {db_use_ssl}")
    print(f"DB_SSL_CA = {db_ssl_ca}")
    print(f"DB_HOST = {db_host}")
    
    if db_use_ssl:
        if not db_ssl_ca:
            print("\n❌ PROBLEM: DB_USE_SSL=True but DB_SSL_CA is not set!")
            print("   Solution: Either set DB_USE_SSL=False or download RDS CA bundle")
        elif not os.path.exists(db_ssl_ca):
            print(f"\n❌ PROBLEM: DB_SSL_CA={db_ssl_ca} but file doesn't exist!")
            print("   Solution: Download the RDS CA bundle")
        else:
            print(f"\n✓ SSL configuration looks correct")
    else:
        print("\n✓ SSL is disabled - should work if RDS allows non-SSL connections")
    
    return db_use_ssl, db_ssl_ca

def test_mysql_connection():
    """Test MySQL connection directly"""
    print("\n" + "=" * 60)
    print("3. Testing MySQL Connection")
    print("=" * 60)
    
    try:
        import MySQLdb
        
        db_host = config('DB_HOST', default='localhost')
        db_user = config('DB_USER', default='')
        db_password = config('DB_PASSWORD', default='')
        db_name = config('DB_NAME', default='amu_pay_db')
        db_port = int(config('DB_PORT', default='3306'))
        
        print(f"Attempting connection to {db_host}:{db_port}...")
        
        # Try without SSL first
        try:
            conn = MySQLdb.connect(
                host=db_host,
                user=db_user,
                passwd=db_password,
                db=db_name,
                port=db_port,
            )
            print("✓ Connection successful WITHOUT SSL")
            conn.close()
            return True
        except Exception as e:
            print(f"✗ Connection failed WITHOUT SSL: {e}")
            
            # Try with SSL
            db_use_ssl = config('DB_USE_SSL', default=False, cast=bool)
            if db_use_ssl:
                db_ssl_ca = config('DB_SSL_CA', default=None)
                ssl_config = {}
                if db_ssl_ca and os.path.exists(db_ssl_ca):
                    ssl_config = {'ca': db_ssl_ca}
                
                try:
                    conn = MySQLdb.connect(
                        host=db_host,
                        user=db_user,
                        passwd=db_password,
                        db=db_name,
                        port=db_port,
                        ssl=ssl_config if ssl_config else None,
                    )
                    print("✓ Connection successful WITH SSL")
                    conn.close()
                    return True
                except Exception as e2:
                    print(f"✗ Connection failed WITH SSL: {e2}")
                    print("\n❌ Both SSL and non-SSL connections failed!")
                    return False
            
            return False
            
    except ImportError:
        print("✗ MySQLdb not installed. Install with: pip install mysqlclient")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("DATABASE CONNECTION DIAGNOSTIC TOOL")
    print("=" * 60)
    print("\nThis script will help identify why your database connection is failing.\n")
    
    # Check SSL certificates
    cert_exists = test_ssl_certificate_exists()
    
    # Check .env config
    db_use_ssl, db_ssl_ca = check_env_config()
    
    # Test connection
    connection_works = test_mysql_connection()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY & RECOMMENDATIONS")
    print("=" * 60)
    
    if connection_works:
        print("✓ Database connection is working!")
        print("  The issue might be with Django's configuration.")
    else:
        print("❌ Database connection is failing.")
        print("\nRecommended fixes:")
        
        if db_use_ssl and (not db_ssl_ca or not os.path.exists(db_ssl_ca)):
            print("\n1. Download RDS CA bundle:")
            print("   wget https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -O /home/ubuntu/rds-ca-bundle.pem")
            print("   chmod 644 /home/ubuntu/rds-ca-bundle.pem")
            print("   Then add to .env: DB_SSL_CA=/home/ubuntu/rds-ca-bundle.pem")
        
        if db_use_ssl:
            print("\n2. OR disable SSL (if RDS allows it):")
            print("   In .env: DB_USE_SSL=False")
        
        print("\n3. Check RDS Security Group:")
        print("   Ensure your EC2 security group can access RDS on port 3306")
        
        print("\n4. Check RDS parameter group:")
        print("   If require_secure_transport=ON, you MUST use SSL with proper CA")

if __name__ == '__main__':
    main()

