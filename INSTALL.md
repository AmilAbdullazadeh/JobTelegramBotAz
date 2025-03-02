# Installation Guide

This guide will help you set up and run the Job Posting Telegram Bot.

## Prerequisites

- Python 3.8 or higher
- pip3 (Python package installer)
- A Telegram Bot Token (obtained from [@BotFather](https://t.me/BotFather))

## Installation Steps

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd job-posting-telegram-bot
   ```

2. **Create a virtual environment (recommended)**

   ```bash
   python3 -m venv venv
   ```

   Activate the virtual environment:

   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install dependencies**

   ```bash
   pip3 install -r requirements.txt
   ```

4. **Configure the bot**

   Create a `.env` file in the root directory by copying the example:

   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file and add your Telegram Bot Token:

   ```
   TELEGRAM_BOT_TOKEN=7982497609:AAEEshuRIjcPp9UWY784JBfQ-FWbjOO6piI

   ```

5. **Initialize the database**

   ```bash
   python3 init_db.py
   ```

## Running the Bot

Start the bot with:

```bash
python3 run.py
```

The bot will start scraping job websites and listening for commands from Telegram users.

## Testing the Scrapers

You can test if the scrapers are working correctly with:

```bash
python3 test_scrapers.py
```

This will run each scraper and save the results to JSON files for inspection.

## Available Commands

Once the bot is running, you can interact with it on Telegram using these commands:

- `/start` - Start the bot and receive welcome message
- `/help` - Display available commands
- `/filter` - Set up job filters by category or title
- `/showfilters` - Display your current filters
- `/clearfilters` - Remove all your filters
- `/pause` - Pause notifications
- `/resume` - Resume notifications

## Troubleshooting

- If you encounter any issues with the scrapers, check the website structure to ensure it hasn't changed.
- For database issues, try deleting the `data/jobbot.db` file and running `python3 init_db.py` again.
- Check the `bot.log` file for detailed error messages. 