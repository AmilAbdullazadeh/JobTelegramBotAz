# Deployment Guide for Job Posting Telegram Bot

This guide provides multiple options for deploying the Job Posting Telegram Bot.

## Prerequisites

- Python 3.8 or higher
- pip3 (Python package installer)
- A Telegram Bot Token (obtained from [@BotFather](https://t.me/BotFather))

## Option 1: Standard Deployment (Linux/macOS)

### Automated Deployment

1. Make the deployment script executable:
   ```bash
   chmod +x deploy.sh
   ```

2. Run the deployment script:
   ```bash
   ./deploy.sh
   ```

3. Follow the prompts to complete the setup.

### Manual Deployment

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

4. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file and add your Telegram Bot Token.

6. Initialize the database:
   ```bash
   python3 init_db.py
   ```

7. Run the bot:
   ```bash
   python3 run.py
   ```

## Option 2: Systemd Service (Linux)

For a more robust deployment on Linux systems with systemd:

1. Follow steps 1-6 from the Manual Deployment section.

2. Create a systemd service file:
   ```bash
   sudo nano /etc/systemd/system/jobbot.service
   ```

3. Add the following content (replace paths as needed):
   ```
   [Unit]
   Description=Job Posting Telegram Bot
   After=network.target

   [Service]
   Type=simple
   User=<your-username>
   WorkingDirectory=/path/to/bot
   ExecStart=/path/to/bot/venv/bin/python /path/to/bot/run.py
   Restart=on-failure
   RestartSec=10
   StandardOutput=journal
   StandardError=journal

   [Install]
   WantedBy=multi-user.target
   ```

4. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable jobbot.service
   sudo systemctl start jobbot.service
   ```

5. Check the status:
   ```bash
   sudo systemctl status jobbot.service
   ```

## Option 3: Docker Deployment

For containerized deployment using Docker:

1. Make sure Docker and Docker Compose are installed on your system.

2. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file and add your Telegram Bot Token.

4. Build and start the container:
   ```bash
   docker-compose up -d
   ```

5. Check the logs:
   ```bash
   docker-compose logs -f
   ```

### Docker Management Commands

- Stop the bot:
  ```bash
  docker-compose down
  ```

- Restart the bot:
  ```bash
  docker-compose restart
  ```

- Update after code changes:
  ```bash
  docker-compose down
  docker-compose build
  docker-compose up -d
  ```

## Option 4: Cloud Deployment

### Heroku Deployment

1. Install the Heroku CLI and log in.

2. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```

3. Add a Procfile (create a file named `Procfile` with no extension):
   ```
   worker: python3 run.py
   ```

4. Set environment variables:
   ```bash
   heroku config:set TELEGRAM_BOT_TOKEN=your_token_here
   ```

5. Deploy to Heroku:
   ```bash
   git push heroku main
   ```

6. Scale the worker dyno:
   ```bash
   heroku ps:scale worker=1
   ```

### AWS EC2 Deployment

1. Launch an EC2 instance with Ubuntu.

2. Connect to your instance via SSH.

3. Install required packages:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv git
   ```

4. Clone the repository:
   ```bash
   git clone <repository-url>
   cd job-posting-telegram-bot
   ```

5. Follow the Standard Deployment steps above.

## Monitoring and Maintenance

### Logs

- Standard deployment: Check the `bot.log` file.
- Systemd service: `sudo journalctl -u jobbot.service`
- Docker: `docker-compose logs -f`

### Database Backup

To back up the SQLite database:

```bash
cp data/jobbot.db data/jobbot.db.backup
```

### Updating the Bot

1. Pull the latest changes:
   ```bash
   git pull
   ```

2. Restart the service:
   - Standard: Restart the Python process
   - Systemd: `sudo systemctl restart jobbot.service`
   - Docker: `docker-compose down && docker-compose up -d`

## Troubleshooting

### Bot Not Responding

1. Check if the bot is running:
   ```bash
   ps aux | grep run.py
   ```

2. Check the logs for errors.

3. Verify your Telegram Bot Token is correct.

### Scraper Issues

If the scrapers are not working correctly:

1. Run the test script:
   ```bash
   python3 test_scrapers.py
   ```

2. Check if the website structure has changed and update the scrapers accordingly.

### Database Issues

If you encounter database issues:

1. Back up the current database.
2. Delete the database file: `rm data/jobbot.db`
3. Reinitialize the database: `python3 init_db.py` 