#!/bin/bash
# Database backup script for Job Posting Telegram Bot

# Set backup directory
BACKUP_DIR="./backups"
DB_FILE="./data/jobbot.db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/jobbot_${TIMESTAMP}.db"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if database file exists
if [ ! -f "$DB_FILE" ]; then
    echo "Error: Database file not found at $DB_FILE"
    exit 1
fi

# Create backup
echo "Creating backup of database..."
cp "$DB_FILE" "$BACKUP_FILE"

# Compress backup
echo "Compressing backup..."
gzip "$BACKUP_FILE"

# Cleanup old backups (keep last 10)
echo "Cleaning up old backups..."
ls -t "${BACKUP_DIR}"/jobbot_*.db.gz | tail -n +11 | xargs -r rm

echo "Backup completed: ${BACKUP_FILE}.gz"
echo "Total backups: $(ls "${BACKUP_DIR}"/jobbot_*.db.gz | wc -l)" 