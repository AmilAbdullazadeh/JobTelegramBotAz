#!/bin/bash
# Update script for Job Posting Telegram Bot

set -e  # Exit on error

echo "===== Job Posting Telegram Bot Update ====="
echo "Starting update process..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install git to update the bot."
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "This doesn't appear to be a git repository. Cannot update."
    exit 1
fi

# Backup the database
echo "Backing up the database..."
./backup_db.sh

# Pull latest changes
echo "Pulling latest changes from repository..."
git pull

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    # Update dependencies
    echo "Updating dependencies..."
    pip3 install -r requirements.txt
fi

# Check if running as systemd service
if systemctl is-active --quiet jobbot.service; then
    echo "Restarting systemd service..."
    sudo systemctl restart jobbot.service
    echo "Service restarted."
else
    echo "Bot is not running as a systemd service."
    echo "To restart the bot, run: python3 run.py"
fi

echo "===== Update completed =====" 