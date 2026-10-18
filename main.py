import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import BOT_TOKEN, GEMINI_API_KEY
from bot.handlers import (
    start,
    help_command,
    privacy_command,
    game_command,
    ask,
    clear_memory,
    memory_command,
    forget_memory,
    forget_all,
    stats,
    chat_message,
    button_handler,
    voice_message,
    welcome_new_member,
    goodbye_member,
)

# Logging Setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

def main():
    if not BOT_TOKEN or not GEMINI_API_KEY:
        print("❌ CRITICAL ERROR: BOT_TOKEN or GEMINI_API_KEY missing in environment variables!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("privacy", privacy_command))
    app.add_handler(CommandHandler("game", game_command))
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(CommandHandler("clear", clear_memory))
    app.add_handler(CommandHandler("memory", memory_command))
    app.add_handler(CommandHandler("forget", forget_memory))
    app.add_handler(CommandHandler("forget_all", forget_all))
    app.add_handler(CommandHandler("stats", stats))

    # Chat & Voice Handlers
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat_message))
    app.add_handler(MessageHandler(filters.VOICE, voice_message))
    
    # Member Join/Leave Handlers
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye_member))

    # Callback Query (Inline Buttons) Handler
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 SARKAR Bot successfully start ho gaya hai! ✨🌸")
    app.run_polling()

if __name__ == "__main__":
    main()
