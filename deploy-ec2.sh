#!/bin/bash

# AWS EC2 Deployment Script for API Comparator
# Run this script on your EC2 instance after connecting via SSH

set -e  # Exit on error

echo "======================================"
echo "API Comparator - EC2 Deployment Script"
echo "======================================"
echo ""

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
echo "🐍 Installing Python and pip..."
sudo apt install -y python3-pip python3-venv git

# Create application directory
APP_DIR="$HOME/api-comparator"
echo "📁 Creating application directory at $APP_DIR..."
mkdir -p $APP_DIR
cd $APP_DIR

# If files are not already present, prompt user
if [ ! -f "requirements.txt" ]; then
    echo ""
    echo "⚠️  Application files not found!"
    echo "Please upload your application files to $APP_DIR"
    echo ""
    echo "You can use one of these methods:"
    echo "1. SCP: scp -i your-key.pem -r /local/path/* ubuntu@$HOSTNAME:$APP_DIR/"
    echo "2. Git: git clone your-repository-url $APP_DIR"
    echo ""
    exit 1
fi

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create data directory
echo "💾 Creating data directory..."
mkdir -p data

# Create systemd service file
echo "⚙️  Creating systemd service..."
sudo tee /etc/systemd/system/api-comparator.service > /dev/null <<EOF
[Unit]
Description=API Comparator Streamlit App
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Enable and start service
echo "🚀 Enabling and starting API Comparator service..."
sudo systemctl enable api-comparator
sudo systemctl start api-comparator

# Wait a moment for the service to start
sleep 3

# Check service status
echo ""
echo "✅ Deployment complete!"
echo ""
echo "======================================"
echo "Service Status:"
echo "======================================"
sudo systemctl status api-comparator --no-pager

echo ""
echo "======================================"
echo "Access Information:"
echo "======================================"
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com)
echo "🌐 Application URL: http://$PUBLIC_IP:8501"
echo ""
echo "Useful Commands:"
echo "  View logs:     sudo journalctl -u api-comparator -f"
echo "  Restart:       sudo systemctl restart api-comparator"
echo "  Stop:          sudo systemctl stop api-comparator"
echo "  Status:        sudo systemctl status api-comparator"
echo ""
echo "⚠️  Make sure Security Group allows inbound traffic on port 8501!"
echo ""
