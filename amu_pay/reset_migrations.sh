#!/bin/bash

# Django Migration Reset Script for AMU_Pay
# This script helps reset migrations when deploying on a new device
# WARNING: This will delete your local database and migrations!

echo "========================================="
echo "AMU_Pay Migration Reset Script"
echo "========================================="
echo ""
echo "WARNING: This script will delete:"
echo "  - All migration files (except __init__.py)"
echo "  - Your local database (db.sqlite3 or database)"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Operation cancelled."
    exit 0
fi

# Navigate to project directory
cd "$(dirname "$0")"

echo ""
echo "Step 1: Removing all migration files..."
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

echo ""
echo "Step 2: Removing database..."
rm -f db.sqlite3

echo ""
echo "Step 3: Creating fresh migrations..."
python manage.py makemigrations

echo ""
echo "Step 4: Applying migrations..."
python manage.py migrate

echo ""
echo "Step 5: Creating superuser..."
echo "You can now create a superuser with: python manage.py createsuperuser"
echo ""
echo "========================================="
echo "Migration reset complete!"
echo "========================================="

