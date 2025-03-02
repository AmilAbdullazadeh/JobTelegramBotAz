#!/bin/bash
# Deployment script for Job Posting Telegram Bot

set -e  # Exit on error

echo "===== Job Posting Telegram Bot Deployment ====="
echo "Starting deployment process..."

# Check if Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "Python version must be 3.8 or higher. Current version: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install or upgrade dependencies
echo "Installing dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit the .env file with your Telegram Bot Token."
    echo "Press Enter to continue after editing the file..."
    read
fi

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    echo "Creating data directory..."
    mkdir -p data
fi

# Initialize the database
echo "Initializing database..."
python3 init_db.py

# Create systemd service file
echo "Creating systemd service file..."
cat > jobbot.service << EOF
[Unit]
Description=Job Posting Telegram Bot
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python $(pwd)/run.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "Systemd service file created: jobbot.service"
echo "To install the service, run:"
echo "sudo cp jobbot.service /etc/systemd/system/"
echo "sudo systemctl daemon-reload"
echo "sudo systemctl enable jobbot.service"
echo "sudo systemctl start jobbot.service"

echo "===== Deployment completed ====="
echo "You can now run the bot with: python run.py"
echo "Or install and start the systemd service as described above." 