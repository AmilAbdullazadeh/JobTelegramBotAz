#!/bin/bash
# Installation verification script for Job Posting Telegram Bot

set -e  # Exit on error

echo "===== Job Posting Telegram Bot Installation Verification ====="

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo "✅ Python version: $PYTHON_VERSION"
    
    if [ "$(echo "$PYTHON_VERSION" | cut -d. -f1)" -lt 3 ] || ([ "$(echo "$PYTHON_VERSION" | cut -d. -f1)" -eq 3 ] && [ "$(echo "$PYTHON_VERSION" | cut -d. -f2)" -lt 8 ]); then
        echo "⚠️ Warning: Python version should be 3.8 or higher."
    fi
else
    echo "❌ Python 3 not found."
    exit 1
fi

# Check if virtual environment exists
echo "Checking virtual environment..."
if [ -d "venv" ]; then
    echo "✅ Virtual environment exists."
else
    echo "⚠️ Virtual environment not found. It's recommended to use a virtual environment."
fi

# Check required files
echo "Checking required files..."
REQUIRED_FILES=("run.py" "requirements.txt" "src/main.py" "src/bot.py" "src/scrapers.py" "src/models.py" "src/db_manager.py" "src/config.py")
MISSING_FILES=0

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists."
    else
        echo "❌ $file is missing!"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ $MISSING_FILES -gt 0 ]; then
    echo "⚠️ Warning: $MISSING_FILES required files are missing."
fi

# Check .env file
echo "Checking environment configuration..."
if [ -f ".env" ]; then
    echo "✅ .env file exists."
    
    # Check if TELEGRAM_BOT_TOKEN is set
    if grep -q "TELEGRAM_BOT_TOKEN=" .env && ! grep -q "TELEGRAM_BOT_TOKEN=$" .env; then
        echo "✅ TELEGRAM_BOT_TOKEN is set."
    else
        echo "❌ TELEGRAM_BOT_TOKEN is not set in .env file."
    fi
else
    echo "❌ .env file is missing."
    echo "  Please create a .env file based on .env.example."
fi

# Check data directory
echo "Checking data directory..."
if [ -d "data" ]; then
    echo "✅ data directory exists."
else
    echo "⚠️ data directory not found. It will be created when the bot runs."
fi

# Check if database exists
echo "Checking database..."
if [ -f "data/jobbot.db" ]; then
    echo "✅ Database file exists."
else
    echo "⚠️ Database file not found. It will be created when the bot runs."
fi

# Check if deployment scripts are executable
echo "Checking deployment scripts..."
SCRIPTS=("deploy.sh" "backup_db.sh" "update.sh" "monitor.sh" "healthcheck.sh" "setup_cron.sh")
for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            echo "✅ $script is executable."
        else
            echo "⚠️ $script is not executable. Run: chmod +x $script"
        fi
    else
        echo "⚠️ $script not found."
    fi
done

# Check if required Python packages are installed
echo "Checking Python dependencies..."
if [ -d "venv" ]; then
    source venv/bin/activate
fi

MISSING_PACKAGES=0
REQUIRED_PACKAGES=("python-telegram-bot" "requests" "beautifulsoup4" "lxml" "SQLAlchemy" "schedule" "python-dotenv")

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        echo "✅ $package is installed."
    else
        echo "❌ $package is not installed."
        MISSING_PACKAGES=$((MISSING_PACKAGES + 1))
    fi
done

if [ $MISSING_PACKAGES -gt 0 ]; then
    echo "⚠️ Warning: $MISSING_PACKAGES required packages are missing."
    echo "  Run: pip3 install -r requirements.txt"
fi

echo "===== Verification completed ====="

if [ $MISSING_FILES -eq 0 ] && [ $MISSING_PACKAGES -eq 0 ] && [ -f ".env" ] && grep -q "TELEGRAM_BOT_TOKEN=" .env && ! grep -q "TELEGRAM_BOT_TOKEN=$" .env; then
    echo "✅ Installation looks good! You can run the bot with: python3 run.py"
else
    echo "⚠️ Some issues were found. Please fix them before running the bot." 