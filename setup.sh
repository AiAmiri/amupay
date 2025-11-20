#!/bin/bash

# AMU Pay EC2 Deployment Setup Script
# This script sets up the environment for deploying Django application on EC2

set -e  # Exit on any error

echo "========================================="
echo "AMU Pay EC2 Deployment Setup"
echo "========================================="

# Update system packages
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and pip
echo "Installing Python 3.11 and pip..."
sudo apt-get install -y python3.11 python3.11-venv python3-pip

# Install MySQL client and development libraries
echo "Installing MySQL client libraries..."
sudo apt-get install -y default-libmysqlclient-dev build-essential pkg-config

# Install Nginx
echo "Installing Nginx..."
sudo apt-get install -y nginx

# Install MySQL Server (if not using RDS)
read -p "Do you want to install MySQL Server locally? (y/n): " install_mysql
if [ "$install_mysql" = "y" ]; then
    echo "Installing MySQL Server..."
    sudo apt-get install -y mysql-server
    echo "Please configure MySQL root password when prompted."
fi

# Create application directory
APP_DIR="/home/ubuntu/amu_pay"
echo "Creating application directory at $APP_DIR..."
mkdir -p $APP_DIR
cd $APP_DIR/amu_pay || cd $APP_DIR

# Create virtual environment
echo "Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
if [ -f "amu_pay/requirements.txt" ]; then
    pip install -r amu_pay/requirements.txt
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Error: requirements.txt not found!"
    exit 1
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p staticfiles media
mkdir -p /var/log/gunicorn
mkdir -p /var/run/gunicorn

# Set permissions
echo "Setting permissions..."
sudo chown -R ubuntu:ubuntu $APP_DIR
sudo chown -R ubuntu:ubuntu /var/log/gunicorn
sudo chown -R ubuntu:ubuntu /var/run/gunicorn

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file from env.example..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "Please edit .env file with your actual configuration values."
    else
        echo "Warning: env.example not found. Please create .env file manually."
    fi
fi

# Setup Nginx
echo "Setting up Nginx..."
if [ -f nginx.conf ]; then
    sudo cp nginx.conf /etc/nginx/sites-available/amu_pay
    sudo ln -sf /etc/nginx/sites-available/amu_pay /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t
    echo "Nginx configuration updated. Restart with: sudo systemctl restart nginx"
else
    echo "Warning: nginx.conf not found."
fi

# Setup systemd service
echo "Setting up systemd service..."
if [ -f amu_pay.service ]; then
    sudo cp amu_pay.service /etc/systemd/system/
    sudo systemctl daemon-reload
    echo "Systemd service installed. Enable with: sudo systemctl enable amu_pay"
    echo "Start with: sudo systemctl start amu_pay"
else
    echo "Warning: amu_pay.service not found."
fi

echo "========================================="
echo "Setup completed!"
echo "========================================="
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run database migrations: python manage.py migrate"
echo "3. Create superuser: python manage.py createsuperuser"
echo "4. Collect static files: python manage.py collectstatic"
echo "5. Start the service: sudo systemctl start amu_pay"
echo "6. Enable service on boot: sudo systemctl enable amu_pay"
echo "7. Start Nginx: sudo systemctl start nginx"
echo "8. Enable Nginx on boot: sudo systemctl enable nginx"

