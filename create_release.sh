#!/bin/bash
# Create a release package for Job Posting Telegram Bot

set -e  # Exit on error

echo "===== Creating release package for Job Posting Telegram Bot ====="

# Get version from user
echo "Enter release version (e.g., 1.0.0):"
read VERSION

# Create release directory
RELEASE_DIR="release_${VERSION}"
mkdir -p "$RELEASE_DIR"

# Copy source files
echo "Copying source files..."
cp -r src "$RELEASE_DIR/"
cp run.py init_db.py requirements.txt .env.example README.md "$RELEASE_DIR/"

# Copy deployment files
echo "Copying deployment files..."
cp deploy.sh backup_db.sh update.sh monitor.sh healthcheck.sh setup_cron.sh verify_installation.sh "$RELEASE_DIR/"
cp Dockerfile docker-compose.yml Procfile "$RELEASE_DIR/"
cp DEPLOYMENT.md "$RELEASE_DIR/"

# Make scripts executable
echo "Making scripts executable..."
chmod +x "$RELEASE_DIR"/*.sh

# Create version file
echo "Creating version file..."
echo "version=$VERSION" > "$RELEASE_DIR/version.txt"
echo "release_date=$(date +"%Y-%m-%d")" >> "$RELEASE_DIR/version.txt"

# Create archive
echo "Creating archive..."
tar -czf "jobbot_${VERSION}.tar.gz" "$RELEASE_DIR"

# Clean up
echo "Cleaning up..."
rm -rf "$RELEASE_DIR"

echo "===== Release package created: jobbot_${VERSION}.tar.gz ====="
echo "To deploy, extract the archive and follow the instructions in DEPLOYMENT.md" 