#!/bin/bash
# Setup cron jobs for Job Posting Telegram Bot

set -e  # Exit on error

echo "===== Setting up cron jobs for Job Posting Telegram Bot ====="

# Get absolute path to the bot directory
BOT_DIR=$(pwd)

# Create temporary crontab file
TEMP_CRONTAB=$(mktemp)

# Export current crontab
crontab -l > "$TEMP_CRONTAB" 2>/dev/null || echo "# Job Posting Telegram Bot cron jobs" > "$TEMP_CRONTAB"

# Add backup job (daily at 3:00 AM)
if ! grep -q "backup_db.sh" "$TEMP_CRONTAB"; then
    echo "Adding daily database backup job..."
    echo "0 3 * * * cd $BOT_DIR && ./backup_db.sh >> $BOT_DIR/cron.log 2>&1" >> "$TEMP_CRONTAB"
fi

# Add monitoring job (every hour)
if ! grep -q "monitor.sh" "$TEMP_CRONTAB"; then
    echo "Adding hourly monitoring job..."
    echo "0 * * * * cd $BOT_DIR && ./monitor.sh >> $BOT_DIR/cron.log 2>&1" >> "$TEMP_CRONTAB"
fi

# Add health check job (every 15 minutes)
if ! grep -q "healthcheck.sh" "$TEMP_CRONTAB"; then
    echo "Adding health check job (runs every 15 minutes)..."
    echo "*/15 * * * * cd $BOT_DIR && ./healthcheck.sh >> $BOT_DIR/cron.log 2>&1" >> "$TEMP_CRONTAB"
fi

# Add weekly update check (Sunday at 4:00 AM)
if ! grep -q "update.sh" "$TEMP_CRONTAB"; then
    echo "Adding weekly update check job..."
    echo "0 4 * * 0 cd $BOT_DIR && ./update.sh >> $BOT_DIR/cron.log 2>&1" >> "$TEMP_CRONTAB"
fi

# Install new crontab
echo "Installing crontab..."
crontab "$TEMP_CRONTAB"

# Clean up
rm "$TEMP_CRONTAB"

echo "Cron jobs installed successfully."
echo "You can view the cron log at: $BOT_DIR/cron.log"
echo "To view current cron jobs, run: crontab -l" 