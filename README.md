# API Testing & Comparison Tool

A lightweight Python application for testing and comparing API responses across different versions. Perfect for ensuring API changes don't break functionality.

## 🎯 Features

- **API Configuration Management**: Save multiple API endpoints with authentication
- **Test Execution**: Execute API calls with different parameters
- **Response Storage**: Save responses with test case names
- **Side-by-Side Comparison**: Compare responses from "Before" and "After" API versions
- **Detailed Diff Analysis**: Identify exact differences in JSON responses
- **Test History**: View all previous test executions
- **Simple UI**: Streamlit-based interface (no complex frontend needed)

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## 🚀 Quick Start (Local Development)

### 1. Clone or Download the Project

```bash
cd api-comparator
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 How to Use

### Step 1: Configure Your APIs

1. Go to **API Configuration** menu
2. Add your "Before Change" API:
   - Task Name: e.g., "GetFlight_Comparison"
   - API Version: "Before Change"
   - API Endpoint: Your old API URL
   - Authentication: Choose type and provide credentials
   - HTTP Method: GET/POST/PUT/DELETE

3. Add your "After Change" API:
   - Same task name: "GetFlight_Comparison"
   - API Version: "After Change"
   - API Endpoint: Your new API URL
   - (Same authentication and method)

### Step 2: Execute Tests

1. Go to **Execute Tests** menu
2. Select your task and API version
3. Enter a test case name (e.g., "Test_ValidFlight")
4. Provide request payload (JSON)
5. Click "Execute Test"
6. Repeat for different test cases with different parameters

### Step 3: Compare Results

1. Go to **Compare Results** menu
2. Select your task
3. Select a test case
4. View side-by-side comparison
5. See detailed differences highlighted

## 🔧 Configuration

Edit `config.py` to customize:
- Default timeout
- Database path
- UI settings

## 📁 Project Structure

```
api-comparator/
├── app.py                 # Main Streamlit application
├── api_manager.py         # API request handling
├── database.py            # SQLite database operations
├── comparator.py          # Response comparison logic
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
└── data/
    └── api_tests.db      # SQLite database (auto-created)
```

## 🌐 AWS EC2 Deployment

### Prerequisites

- AWS Account
- EC2 instance (t2.micro or larger)
- Ubuntu 22.04 LTS or similar

### Step 1: Launch EC2 Instance

1. Log in to AWS Console
2. Navigate to EC2 > Launch Instance
3. Choose:
   - **AMI**: Ubuntu Server 22.04 LTS
   - **Instance Type**: t2.micro (or t2.small for better performance)
   - **Key Pair**: Create or select existing
   - **Security Group**: Create new with following rules:
     - SSH (Port 22) - Your IP
     - Custom TCP (Port 8501) - Anywhere (0.0.0.0/0)
4. Launch instance

### Step 2: Connect to EC2

```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### Step 3: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3-pip python3-venv -y

# Install git (if you're using git)
sudo apt install git -y
```

### Step 4: Deploy Application

```bash
# Create application directory
mkdir -p ~/api-comparator
cd ~/api-comparator

# Upload your files using SCP (from your local machine)
# scp -i your-key.pem -r * ubuntu@your-ec2-public-ip:~/api-comparator/

# OR if using git:
# git clone your-repository-url .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 5: Run with systemd (Production)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/api-comparator.service
```

Add the following content:

```ini
[Unit]
Description=API Comparator Streamlit App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/api-comparator
Environment="PATH=/home/ubuntu/api-comparator/venv/bin"
ExecStart=/home/ubuntu/api-comparator/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable api-comparator

# Start the service
sudo systemctl start api-comparator

# Check status
sudo systemctl status api-comparator
```

### Step 6: Access Your Application

Open your browser and navigate to:
```
http://your-ec2-public-ip:8501
```

### Managing the Service

```bash
# Stop the service
sudo systemctl stop api-comparator

# Restart the service
sudo systemctl restart api-comparator

# View logs
sudo journalctl -u api-comparator -f
```

## 🔒 Security Best Practices

### 1. Use HTTPS (Recommended)

Install Nginx and Certbot:

```bash
sudo apt install nginx certbot python3-certbot-nginx -y
```

Configure Nginx:

```bash
sudo nano /etc/nginx/sites-available/api-comparator
```

Add:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/api-comparator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 2. Restrict Access

Update Security Group to allow only your IP addresses.

### 3. Add Authentication

Consider adding Streamlit authentication or using AWS Cognito.

## 🐛 Troubleshooting

### Application won't start

```bash
# Check logs
sudo journalctl -u api-comparator -n 50

# Check if port is in use
sudo netstat -tulpn | grep 8501

# Restart service
sudo systemctl restart api-comparator
```

### Can't access from browser

1. Check Security Group allows port 8501
2. Check EC2 instance is running
3. Verify public IP address
4. Check service status: `sudo systemctl status api-comparator`

### Database errors

```bash
# Check database file permissions
ls -la data/api_tests.db

# Recreate database
rm data/api_tests.db
# Restart application - it will recreate the database
```

## 🔄 Updates and Maintenance

```bash
# Pull latest changes (if using git)
cd ~/api-comparator
git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart api-comparator
```

## 💾 Backup

```bash
# Backup database
cp ~/api-comparator/data/api_tests.db ~/api_tests_backup_$(date +%Y%m%d).db

# Or create a backup script
crontab -e
# Add: 0 2 * * * cp ~/api-comparator/data/api_tests.db ~/backups/api_tests_$(date +\%Y\%m\%d).db
```

## 📊 Monitoring

```bash
# Monitor application logs
tail -f /var/log/syslog | grep streamlit

# Monitor system resources
htop

# Check application status
sudo systemctl status api-comparator
```

## 🤝 Support

For issues or questions, check the logs:
```bash
sudo journalctl -u api-comparator -f
```

## 📝 License

This project is open source and available for personal and commercial use.

---

**Built with ❤️ using Python & Streamlit**
