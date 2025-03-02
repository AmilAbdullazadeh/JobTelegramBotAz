import logging
import os
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
        
        await update.message.reply_text(
            f"👋 Hello {user.first_name}!\n\n"
            f"I'm your Job Posting Bot. I'll notify you about new job postings from:\n"
            f"• JobSearch.az\n"
            f"• HelloJob.az\n"
            f"• SmartJob.az\n\n"
            f"You can set up filters to receive only the jobs you're interested in.\n\n"
            f"Use /help to see available commands."
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command"""
        help_text = (
            "🔍 *Job Posting Bot Help*\n\n"
            "*Available Commands:*\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/filter - Set up job filters by category or title\n"
            "/showfilters - Display your current filters\n"
            "/clearfilters - Remove all your filters\n"
            "/pause - Pause notifications\n"
            "/resume - Resume notifications\n\n"
            "*How to use filters:*\n"
            "• *Category filters* - Filter jobs by their category (e.g., IT, Marketing)\n"
            "• *Keyword filters* - Filter jobs by keywords in their title (e.g., Python, Manager)\n\n"
            "If you have both category and keyword filters, jobs must match at least one of each type."
        )
        
        await update.message.reply_text(help_text, parse_mode="Markdown")
    
    async def filter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /filter command to start the filter conversation"""
        keyboard = [
            [
                InlineKeyboardButton("Add Category Filter", callback_data=CATEGORY_FILTER),
                InlineKeyboardButton("Add Keyword Filter", callback_data=KEYWORD_FILTER),
            ],
            [
                InlineKeyboardButton("Remove Filter", callback_data=REMOVE_FILTER),
                InlineKeyboardButton("Cancel", callback_data=CANCEL),
            ],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "What would you like to do?",
            reply_markup=reply_markup
        )
        
        return CHOOSING_FILTER_TYPE
    
    async def category_filter_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle category filter selection"""
        query = update.callback_query
        await query.answer()
        
        # Get available categories
        categories = self.db_manager.get_all_categories()
        
        if categories:
            category_text = "Available categories:\n• " + "\n• ".join(categories)
            await query.edit_message_text(
                f"{category_text}\n\nPlease enter a category name to filter by (or /cancel to abort):"
            )
        else:
            await query.edit_message_text(
                "Please enter a category name to filter by (or /cancel to abort):"
            )
        
        return ADDING_CATEGORY
    
    async def keyword_filter_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle keyword filter selection"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "Please enter a keyword to filter job titles by (or /cancel to abort):"
        )
        
        return ADDING_KEYWORD
    
    async def remove_filter_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle remove filter selection"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        filters = self.db_manager.get_user_filters(user_id)
        
        if not filters or (not filters['categories'] and not filters['keywords']):
            await query.edit_message_text("You don't have any filters set up yet.")
            return ConversationHandler.END
        
        keyboard = []
        
        # Add category filters
        for category in filters['categories']:
            keyboard.append([
                InlineKeyboardButton(
                    f"Category: {category}", 
                    callback_data=f"remove_category_{category}"
                )
            ])
        
        # Add keyword filters
        for keyword in filters['keywords']:
            keyboard.append([
                InlineKeyboardButton(
                    f"Keyword: {keyword}", 
                    callback_data=f"remove_keyword_{keyword}"
                )
            ])
        
        # Add cancel button
        keyboard.append([InlineKeyboardButton("Cancel", callback_data=CANCEL)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Select a filter to remove:",
            reply_markup=reply_markup
        )
        
        return REMOVING_FILTER
    
    async def add_category_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add a category filter"""
        user_id = update.effective_user.id
        category_name = update.message.text.strip()
        
        success = self.db_manager.add_category_filter(user_id, category_name)
        
        if success:
            await update.message.reply_text(
                f"✅ Added category filter: {category_name}\n\n"
                f"You will now receive notifications for jobs in this category."
            )
        else:
            await update.message.reply_text(
                f"You already have a filter for the category: {category_name}"
            )
        
        return ConversationHandler.END
    
    async def add_keyword_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add a keyword filter"""
        user_id = update.effective_user.id
        keyword = update.message.text.strip()
        
        success = self.db_manager.add_keyword_filter(user_id, keyword)
        
        if success:
            await update.message.reply_text(
                f"✅ Added keyword filter: {keyword}\n\n"
                f"You will now receive notifications for jobs with this keyword in the title."
            )
        else:
            await update.message.reply_text(
                f"You already have a filter for the keyword: {keyword}"
            )
        
        return ConversationHandler.END
    
    async def remove_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Remove a filter"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        callback_data = query.data
        
        if callback_data.startswith("remove_category_"):
            category = callback_data.replace("remove_category_", "")
            success = self.db_manager.remove_category_filter(user_id, category)
            
            if success:
                await query.edit_message_text(f"✅ Removed category filter: {category}")
            else:
                await query.edit_message_text(f"Failed to remove category filter: {category}")
                
        elif callback_data.startswith("remove_keyword_"):
            keyword = callback_data.replace("remove_keyword_", "")
            success = self.db_manager.remove_keyword_filter(user_id, keyword)
            
            if success:
                await query.edit_message_text(f"✅ Removed keyword filter: {keyword}")
            else:
                await query.edit_message_text(f"Failed to remove keyword filter: {keyword}")
        
        return ConversationHandler.END
    
    async def cancel_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the filter conversation"""
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            await query.edit_message_text("Filter operation cancelled.")
        else:
            await update.message.reply_text("Filter operation cancelled.")
        
        return ConversationHandler.END
    
    async def show_filters_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /showfilters command"""
        user_id = update.effective_user.id
        filters = self.db_manager.get_user_filters(user_id)
        
        if not filters or (not filters['categories'] and not filters['keywords']):
            await update.message.reply_text(
                "You don't have any filters set up yet.\n\n"
                "Use /filter to add filters."
            )
            return
        
        filter_text = "*Your current filters:*\n\n"
        
        if filters['categories']:
            filter_text += "*Categories:*\n"
            for category in filters['categories']:
                filter_text += f"• {category}\n"
            filter_text += "\n"
        
        if filters['keywords']:
            filter_text += "*Keywords:*\n"
            for keyword in filters['keywords']:
                filter_text += f"• {keyword}\n"
        
        await update.message.reply_text(filter_text, parse_mode="Markdown")
    
    async def clear_filters_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /clearfilters command"""
        user_id = update.effective_user.id
        success = self.db_manager.clear_user_filters(user_id)
        
        if success:
            await update.message.reply_text("✅ All your filters have been cleared.")
        else:
            await update.message.reply_text("Failed to clear filters. Please try again later.")
    
    async def pause_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /pause command"""
        user_id = update.effective_user.id
        success = self.db_manager.set_user_active(user_id, False)
        
        if success:
            await update.message.reply_text(
                "⏸️ Notifications paused. You will no longer receive job updates.\n\n"
                "Use /resume to start receiving notifications again."
            )
        else:
            await update.message.reply_text("Failed to pause notifications. Please try again later.")
    
    async def resume_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /resume command"""
        user_id = update.effective_user.id
        success = self.db_manager.set_user_active(user_id, True)
        
        if success:
            await update.message.reply_text(
                "▶️ Notifications resumed. You will now receive job updates again."
            )
        else:
            await update.message.reply_text("Failed to resume notifications. Please try again later.")
    
    async def send_job_notification(self, user_id, job):
        """Send a job notification to a user"""
        try:
            job_text = (
                f"🔍 *New Job Posting*\n\n"
                f"*{job.title}*\n"
                f"*Company:* {job.company or 'Not specified'}\n"
                f"*Location:* {job.location or 'Not specified'}\n"
                f"*Category:* {job.category.name if job.category else 'Not specified'}\n"
                f"*Source:* {job.source}\n\n"
                f"[View Job]({job.url})"
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