import logging
import os
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)

from src.db_manager import DatabaseManager
from src.config import TELEGRAM_BOT_TOKEN

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Conversation states
CHOOSING_FILTER_TYPE, ADDING_CATEGORY, ADDING_KEYWORD, REMOVING_FILTER = range(4)

# Callback data
CATEGORY_FILTER = "category_filter"
KEYWORD_FILTER = "keyword_filter"
REMOVE_FILTER = "remove_filter"
CANCEL = "cancel"

# Fun job-related emojis
JOB_EMOJIS = ["💼", "👔", "🏢", "💻", "📊", "📈", "🔍", "🚀", "💡", "🌟", "✨", "🎯", "🏆"]

# Fun motivational messages
MOTIVATIONAL_MESSAGES = [
    "Your dream job is just around the corner! 🌈",
    "Success is loading... ⌛",
    "You're going to crush that interview! 💪",
    "Your skills are in high demand! 📈",
    "The perfect job is searching for YOU! 🔍",
    "Your career journey is about to level up! 🚀",
    "Exciting opportunities await! ✨",
    "Your professional adventure continues! 🌟",
    "New job, new possibilities! 🎉",
    "Your talent deserves recognition! 🏆"
]

class JobBot:
    """Telegram bot for job notifications"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up all command and conversation handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("showfilters", self.show_filters_command))
        self.application.add_handler(CommandHandler("clearfilters", self.clear_filters_command))
        self.application.add_handler(CommandHandler("pause", self.pause_command))
        self.application.add_handler(CommandHandler("resume", self.resume_command))
        
        # Filter conversation handler
        filter_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("filter", self.filter_command)],
            states={
                CHOOSING_FILTER_TYPE: [
                    CallbackQueryHandler(self.category_filter_selected, pattern=f"^{CATEGORY_FILTER}$"),
                    CallbackQueryHandler(self.keyword_filter_selected, pattern=f"^{KEYWORD_FILTER}$"),
                    CallbackQueryHandler(self.remove_filter_selected, pattern=f"^{REMOVE_FILTER}$"),
                    CallbackQueryHandler(self.cancel_filter, pattern=f"^{CANCEL}$"),
                ],
                ADDING_CATEGORY: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.add_category_filter),
                    CommandHandler("cancel", self.cancel_filter),
                ],
                ADDING_KEYWORD: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.add_keyword_filter),
                    CommandHandler("cancel", self.cancel_filter),
                ],
                REMOVING_FILTER: [
                    CallbackQueryHandler(self.remove_filter, pattern=r"^remove_category_(.+)$|^remove_keyword_(.+)$"),
                    CallbackQueryHandler(self.cancel_filter, pattern=f"^{CANCEL}$"),
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel_filter)],
        )
        self.application.add_handler(filter_conv_handler)
        
        # Error handler
        self.application.add_error_handler(self.error_handler)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command"""
        user = update.effective_user
        
        # Register user in database
        self.db_manager.register_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Pick random emoji
        emoji = random.choice(JOB_EMOJIS)
        
        await update.message.reply_text(
            f"🎉 *Welcome to JobHunter Bot, {user.first_name}!* 🎉\n\n"
            f"{emoji} I'm your personal job-hunting assistant! I'll be scouting these awesome sites for your dream job:\n"
            f"• 🔍 JobSearch.az\n"
            f"• 👋 HelloJob.az\n"
            f"• 🧠 SmartJob.az\n"
            f"• 💰 PashaBank.az\n"
            f"• 💳 KapitalBank.az\n"
            f"• 🏃‍♂️ Busy.az\n"
            f"• ✨ Glorri.az\n\n"
            f"Let's find you that PERFECT job together! 💪\n\n"
            f"Type /help to see all the cool things I can do for you!\n\n"
            f"{random.choice(MOTIVATIONAL_MESSAGES)}"
        , parse_mode="Markdown")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command"""
        await update.message.reply_text(
            f"🦸‍♂️ *Here's how I can help you land that dream job!* 🦸‍♀️\n\n"
            f"🎮 *Commands:*\n\n"
            f"🚀 /start - Wake me up and let's get hunting!\n"
            f"❓ /help - Show this super helpful message\n"
            f"🎯 /filter - Set up your job preferences (this is where the magic happens!)\n"
            f"👀 /showfilters - See what job filters you've set up\n"
            f"🧹 /clearfilters - Start fresh with no filters\n"
            f"⏸️ /pause - Need a break? Pause notifications\n"
            f"▶️ /resume - Ready for more? Resume notifications\n\n"
            f"✨ *Pro Tip:* The more specific your filters, the better matches you'll get!\n\n"
            f"{random.choice(MOTIVATIONAL_MESSAGES)}"
        , parse_mode="Markdown")
    
    async def filter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /filter command"""
        keyboard = [
            [
                InlineKeyboardButton("🏷️ Filter by Category", callback_data=CATEGORY_FILTER),
                InlineKeyboardButton("🔤 Filter by Keyword", callback_data=KEYWORD_FILTER),
            ],
            [
                InlineKeyboardButton("🗑️ Remove Filters", callback_data=REMOVE_FILTER),
                InlineKeyboardButton("❌ Cancel", callback_data=CANCEL),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 *Let's customize your job hunt!* 🎯\n\n"
            "What kind of filtering magic would you like to do today?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
        return CHOOSING_FILTER_TYPE
    
    async def category_filter_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle category filter selection"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "🏷️ *Category Filter* 🏷️\n\n"
            "What job category are you interested in?\n\n"
            "Examples: IT, Marketing, Finance, Sales, etc.\n\n"
            "Type the category name or /cancel to abort."
        , parse_mode="Markdown")
        
        return ADDING_CATEGORY
    
    async def keyword_filter_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle keyword filter selection"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "🔤 *Keyword Filter* 🔤\n\n"
            "What keyword should I look for in job titles?\n\n"
            "Examples: Developer, Manager, Designer, etc.\n\n"
            "Type the keyword or /cancel to abort."
        , parse_mode="Markdown")
        
        return ADDING_KEYWORD
    
    async def remove_filter_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle remove filter selection"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        filters = self.db_manager.get_user_filters(user_id)
        
        if not filters or (not filters['categories'] and not filters['keywords']):
            await query.edit_message_text(
                "🤷‍♂️ You don't have any filters to remove! 🤷‍♀️\n\n"
                "Use /filter to add some first."
            )
            return ConversationHandler.END
        
        keyboard = []
        
        for category in filters.get('categories', []):
            keyboard.append([
                InlineKeyboardButton(f"🏷️ Category: {category}", callback_data=f"remove_category_{category}")
            ])
        
        for keyword in filters.get('keywords', []):
            keyboard.append([
                InlineKeyboardButton(f"🔤 Keyword: {keyword}", callback_data=f"remove_keyword_{keyword}")
            ])
        
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data=CANCEL)])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🗑️ *Remove Filters* 🗑️\n\n"
            "Select a filter to remove:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
        return REMOVING_FILTER
    
    async def remove_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove a selected filter"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        callback_data = query.data
        
        if callback_data.startswith("remove_category_"):
            category = callback_data.replace("remove_category_", "")
            success = self.db_manager.remove_category_filter(user_id, category)
            filter_type = "category"
            filter_value = category
        else:
            keyword = callback_data.replace("remove_keyword_", "")
            success = self.db_manager.remove_keyword_filter(user_id, keyword)
            filter_type = "keyword"
            filter_value = keyword
        
        if success:
            await query.edit_message_text(
                f"🗑️ Successfully removed {filter_type} filter: *{filter_value}*\n\n"
                f"Your job hunt just got a little broader! 🌈",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                f"😕 Oops! Failed to remove {filter_type} filter: *{filter_value}*\n\n"
                f"Please try again later or contact support.",
                parse_mode="Markdown"
            )
        
        return ConversationHandler.END
    
    async def cancel_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the filter conversation"""
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            await query.edit_message_text("🙌 Filter setup canceled! No changes were made.")
        else:
            await update.message.reply_text("🙌 Filter setup canceled! No changes were made.")
        
        return ConversationHandler.END
    
    async def add_category_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add a category filter"""
        user_id = update.effective_user.id
        category_name = update.message.text.strip()
        
        success = self.db_manager.add_category_filter(user_id, category_name)
        
        if success:
            await update.message.reply_text(
                f"🎯 *Category filter added: {category_name}* 🎯\n\n"
                f"Awesome choice! I'll keep an eye out for jobs in this category.\n\n"
                f"{random.choice(MOTIVATIONAL_MESSAGES)}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"😅 You already have a filter for the category: *{category_name}*\n\n"
                f"You're really interested in this one, aren't you? 😉",
                parse_mode="Markdown"
            )
        
        return ConversationHandler.END
    
    async def add_keyword_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add a keyword filter"""
        user_id = update.effective_user.id
        keyword = update.message.text.strip()
        
        success = self.db_manager.add_keyword_filter(user_id, keyword)
        
        if success:
            await update.message.reply_text(
                f"🔍 *Keyword filter added: {keyword}* 🔍\n\n"
                f"Great choice! I'll hunt for jobs with this keyword in the title.\n\n"
                f"{random.choice(MOTIVATIONAL_MESSAGES)}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"😅 You already have a filter for the keyword: *{keyword}*\n\n"
                f"This must be really important to you! I've got it covered. 👍",
                parse_mode="Markdown"
            )
        
        return ConversationHandler.END
    
    async def show_filters_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /showfilters command"""
        user_id = update.effective_user.id
        filters = self.db_manager.get_user_filters(user_id)
        
        if not filters or (not filters['categories'] and not filters['keywords']):
            await update.message.reply_text(
                "🔎 *Your Filter Settings* 🔍\n\n"
                "You don't have any filters set up yet!\n\n"
                "Use /filter to tell me what kind of jobs you're looking for. 🚀",
                parse_mode="Markdown"
            )
            return
        
        filter_text = "🔎 *Your Job Hunt Preferences* 🔍\n\n"
        
        if filters['categories']:
            filter_text += "*Categories you're interested in:*\n"
            for category in filters['categories']:
                filter_text += f"• 🏷️ {category}\n"
            filter_text += "\n"
        
        if filters['keywords']:
            filter_text += "*Keywords you're looking for:*\n"
            for keyword in filters['keywords']:
                filter_text += f"• 🔤 {keyword}\n"
        
        filter_text += f"\n{random.choice(MOTIVATIONAL_MESSAGES)}"
        
        await update.message.reply_text(filter_text, parse_mode="Markdown")
    
    async def clear_filters_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /clearfilters command"""
        user_id = update.effective_user.id
        success = self.db_manager.clear_user_filters(user_id)
        
        if success:
            await update.message.reply_text(
                "🧹 *All filters cleared!* 🧹\n\n"
                "Starting with a clean slate! Sometimes a fresh start is exactly what we need.\n\n"
                "Ready to set up new filters? Just use the /filter command when you're ready!",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "😕 *Oops!* Something went wrong while clearing your filters.\n\n"
                "Please try again later or contact support if the problem persists.",
                parse_mode="Markdown"
            )
    
    async def pause_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /pause command"""
        user_id = update.effective_user.id
        success = self.db_manager.set_user_active(user_id, False)
        
        if success:
            await update.message.reply_text(
                "⏸️ *Notifications paused* ⏸️\n\n"
                "Taking a break from job hunting? No problem!\n\n"
                "I'll stop sending job notifications for now. When you're ready to jump back in, just use /resume.\n\n"
                "I'll be here when you need me! 😊",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "😕 *Oops!* Something went wrong while pausing your notifications.\n\n"
                "Please try again later or contact support if the problem persists.",
                parse_mode="Markdown"
            )
    
    async def resume_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /resume command"""
        user_id = update.effective_user.id
        success = self.db_manager.set_user_active(user_id, True)
        
        if success:
            await update.message.reply_text(
                "▶️ *Notifications resumed!* ▶️\n\n"
                "Welcome back to the job hunt! 🎉\n\n"
                "I'll start sending you job notifications again. Let's find that perfect opportunity!\n\n"
                f"{random.choice(MOTIVATIONAL_MESSAGES)}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "😕 *Oops!* Something went wrong while resuming your notifications.\n\n"
                "Please try again later or contact support if the problem persists.",
                parse_mode="Markdown"
            )
    
    async def send_job_notification(self, user_id, job):
        """Send a job notification to a user"""
        try:
            # Pick a random emoji for the notification
            emoji = random.choice(JOB_EMOJIS)
            
            # Pick a random motivational message
            motivation = random.choice(MOTIVATIONAL_MESSAGES)
            
            job_text = (
                f"{emoji} *Exciting Job Alert!* {emoji}\n\n"
                f"*{job.title}*\n\n"
                f"*🏢 Company:* {job.company or 'Not specified'}\n"
                f"*📍 Location:* {job.location or 'Not specified'}\n"
                f"*🏷️ Category:* {job.category.name if job.category else 'Not specified'}\n"
                f"*🔍 Source:* {job.source}\n\n"
                f"[👉 View Full Job Details 👈]({job.url})\n\n"
                f"{motivation}"
            )
            
            await self.application.bot.send_message(
                chat_id=user_id,
                text=job_text,
                parse_mode="Markdown",
                disable_web_page_preview=False
            )
            
            logger.info(f"Sent job notification to user {user_id}: {job.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending job notification to user {user_id}: {e}")
            return False
    
    async def notify_users_about_new_jobs(self, jobs, since_timestamp=None):
        """Notify users about new jobs matching their filters"""
        active_users = self.db_manager.get_active_users()
        
        for user in active_users:
            user_jobs = self.db_manager.get_new_jobs_for_user(user.telegram_id, since_timestamp)
            
            for job in user_jobs:
                await self.send_job_notification(user.telegram_id, job)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors in the bot"""
        logger.error(f"Update {update} caused error: {context.error}")
    
    def run(self):
        """Run the bot"""
        logger.info("Starting bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def get_bot():
    """Get a configured bot instance"""
    return JobBot() 