# Job Posting Telegram Bot

A Telegram bot that monitors job postings from multiple Azerbaijani job websites:
- jobsearch.az
- hellojob.az
- smartjob.az
- hr.kapitalbank.az
- careers.pashabank.az
- busy.az
- jobs.glorri.az

## Features

- Real-time monitoring of new job postings
- Filtering options by job category and title
- Instant notifications for new matching jobs
- User preference management

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip3 install -r requirements.txt
   ```
3. Create a `.env` file with your Telegram Bot Token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```
4. Initialize the database:
   ```
   python3 init_db.py
   ```
5. Run the bot:
   ```
   python3 run.py
   ```

## Deployment Options

This bot can be deployed in several ways:

### 1. Standard Deployment (Recommended for Development)

Run the bot directly with Python:
```
python3 run.py
```

### 2. Automated Deployment (Linux/macOS)

Use the deployment script:
```
chmod +x deploy.sh
./deploy.sh
```

### 3. Systemd Service (Linux)

The deployment script will create a systemd service file. To install it:
```
sudo cp jobbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jobbot.service
sudo systemctl start jobbot.service
```

### 4. Docker Deployment

Build and run with Docker Compose:
```
docker-compose up -d
```

### 5. Cloud Deployment

For Heroku deployment, use the provided Procfile:
```
heroku create your-app-name
heroku config:set TELEGRAM_BOT_TOKEN=your_token_here
git push heroku main
heroku ps:scale worker=1
```

For more detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Maintenance

### Monitoring

Check the bot's status:
```
./monitor.sh
```

### Automatic Health Checks

Set up cron jobs for monitoring and automatic restarts:
```
chmod +x setup_cron.sh
./setup_cron.sh
```

### Database Backups

Backup the database:
```
./backup_db.sh
```

### Updates

Update the bot to the latest version:
```
./update.sh
```

## Usage

- `/start` - Start the bot and receive welcome message
- `/help` - Display available commands
- `/filter` - Set up job filters by category or title
- `/showfilters` - Display your current filters
- `/clearfilters` - Remove all your filters
- `/pause` - Pause notifications
- `/resume` - Resume notifications

## Requirements

- Python 3.8+
- Telegram Bot Token (obtained from @BotFather)

## Troubleshooting

If you encounter any issues, run the verification script:
```
./verify_installation.sh
```

For more help, see the [DEPLOYMENT.md](DEPLOYMENT.md) file. 