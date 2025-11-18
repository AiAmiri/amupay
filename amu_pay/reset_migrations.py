"""
Django Migration Reset Script for AMU_Pay (Windows-friendly version)
Run this script to reset migrations when deploying on a new device.
WARNING: This will delete your local database and migrations!
"""

import os
import shutil
import sys
from pathlib import Path

def reset_migrations():
    """Reset all migrations and database"""
    
    print("=" * 50)
    print("AMU_Pay Migration Reset Script")
    print("=" * 50)
    print()
    print("WARNING: This script will delete:")
    print("  - All migration files (except __init__.py)")
    print("  - Your local database (db.sqlite3 or database)")
    print()
    
    confirm = input("Are you sure you want to continue? (yes/no): ")
    if confirm.lower() != "yes":
        print("Operation cancelled.")
        return
    
    # Get project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print()
    print("Step 1: Removing all migration files...")
    
    # Find and remove all migration files except __init__.py
    for migrations_dir in project_dir.rglob("migrations"):
        if migrations_dir.is_dir():
            for file in migrations_dir.iterdir():
                if file.is_file() and file.suffix == '.py' and file.stem != '__init__':
                    file.unlink()
                    print(f"  Deleted: {file}")
                elif file.is_file() and file.suffix == '.pyc':
                    file.unlink()
                    print(f"  Deleted: {file}")
    
    print()
    print("Step 2: Removing database...")
    db_file = project_dir / "db.sqlite3"
    if db_file.exists():
        db_file.unlink()
        print(f"  Deleted: {db_file}")
    
    print()
    print("Step 3: Creating fresh migrations...")
    os.system("python manage.py makemigrations")
    
    print()
    print("Step 4: Applying migrations...")
    os.system("python manage.py migrate")
    
    print()
    print("Step 5: Creating superuser...")
    print("You can now create a superuser with: python manage.py createsuperuser")
    print()
    print("=" * 50)
    print("Migration reset complete!")
    print("=" * 50)

if __name__ == "__main__":
    reset_migrations()

