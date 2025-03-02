#!/bin/bash
# Monitoring script for Job Posting Telegram Bot

echo "===== Job Posting Telegram Bot Monitor ====="
echo "Checking bot status..."

# Check if the bot process is running
BOT_PROCESS=$(ps aux | grep "[p]ython run.py" | wc -l)

if [ $BOT_PROCESS -gt 0 ]; then
    echo "✅ Bot is running."
    
    # Get process details
    echo "Process details:"
    ps aux | grep "[p]ython run.py"
    
    # Check uptime
    PID=$(ps aux | grep "[p]ython run.py" | awk '{print $2}')
    if [ -n "$PID" ]; then
        echo "Process uptime:"
        ps -p $PID -o etime=
    fi
else
    echo "❌ Bot is not running!"
fi

# Check systemd service if available
if command -v systemctl &> /dev/null; then
    if systemctl is-active --quiet jobbot.service; then
        echo "✅ Systemd service is active."
        echo "Service status:"
        systemctl status jobbot.service --no-pager | head -n 20
    else
        echo "❌ Systemd service is not active."
    fi
fi

# Check log file
if [ -f "bot.log" ]; then
    echo "Recent log entries:"
    tail -n 20 bot.log
else
    echo "❌ Log file not found."
fi

# Check database
if [ -f "data/jobbot.db" ]; then
    echo "✅ Database file exists."
    echo "Database size: $(du -h data/jobbot.db | cut -f1)"
    
    # If sqlite3 is available, get some stats
    if command -v sqlite3 &> /dev/null; then
        echo "Database statistics:"
        echo "- Users: $(sqlite3 data/jobbot.db "SELECT COUNT(*) FROM users;")"
        echo "- Jobs: $(sqlite3 data/jobbot.db "SELECT COUNT(*) FROM jobs;")"
        echo "- Categories: $(sqlite3 data/jobbot.db "SELECT COUNT(*) FROM categories;")"
    fi
else
    echo "❌ Database file not found."
fi

# Check disk space
echo "Disk space:"
df -h . | tail -n 1

echo "===== Monitoring completed =====" 