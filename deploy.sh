#!/bin/bash

# AMU Pay Deployment Script
# This script deploys the Django application

set -e  # Exit on any error

echo "========================================="
echo "AMU Pay Deployment"
echo "========================================="

APP_DIR="/home/ubuntu/amu_pay"
cd $APP_DIR

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Pull latest code (if using git)
# echo "Pulling latest code..."
# git pull origin main

# Install/update dependencies
echo "Installing/updating dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Restart application service
echo "Restarting application service..."
sudo systemctl restart amu_pay

# Check service status
echo "Checking service status..."
sudo systemctl status amu_pay --no-pager

# Reload Nginx
echo "Reloading Nginx..."
sudo systemctl reload nginx

echo "========================================="
echo "Deployment completed!"
echo "========================================="

