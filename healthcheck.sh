#!/bin/bash
# Health check script for Job Posting Telegram Bot

echo "===== Job Posting Telegram Bot Health Check ====="
echo "Running health check at $(date)"

# Check if the bot process is running
BOT_PROCESS=$(ps aux | grep "[p]ython run.py" | wc -l)

# Check if running as systemd service
SYSTEMD_ACTIVE=false
if command -v systemctl &> /dev/null; then
    if systemctl is-active --quiet jobbot.service; then
        SYSTEMD_ACTIVE=true
    fi
fi

# If bot is not running, restart it
if [ $BOT_PROCESS -eq 0 ] && [ "$SYSTEMD_ACTIVE" = false ]; then
    echo "❌ Bot is not running! Attempting to restart..."
    
    # Check if we're in a virtual environment
    if [ -d "venv" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    fi
    
    # Start the bot in the background
    echo "Starting bot..."
    nohup python3 run.py > bot_restart.log 2>&1 &
    
    # Wait a moment and check if it started
    sleep 5
    if [ $(ps aux | grep "[p]ython run.py" | wc -l) -gt 0 ]; then
        echo "✅ Bot restarted successfully."
    else
        echo "❌ Failed to restart bot. Check bot_restart.log for details."
    fi
elif [ "$SYSTEMD_ACTIVE" = false ] && [ $BOT_PROCESS -gt 0 ]; then
    echo "✅ Bot is running normally."
fi

# If running as systemd service and it's inactive, restart it
if command -v systemctl &> /dev/null; then
    if ! systemctl is-active --quiet jobbot.service; then
        echo "❌ Systemd service is not active! Attempting to restart..."
        sudo systemctl restart jobbot.service
        
        # Check if restart was successful
        if systemctl is-active --quiet jobbot.service; then
            echo "✅ Systemd service restarted successfully."
        else
            echo "❌ Failed to restart systemd service."
            echo "Service status:"
            systemctl status jobbot.service --no-pager
        fi
    elif [ "$SYSTEMD_ACTIVE" = true ]; then
        echo "✅ Systemd service is running normally."
    fi
fi

echo "Health check completed at $(date)" 