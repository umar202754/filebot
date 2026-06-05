import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from handlers.start import start_handler
from handlers.convert import convert_handler
from handlers.premium import premium_handler, payment_callback
from database.db import init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

def main():
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN topilmadi! .env faylini tekshiring.")

    init_db()
    print("✅ Ma'lumotlar bazasi tayyor")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",   start_handler))
    app.add_handler(CommandHandler("premium", premium_handler))
    app.add_handler(CommandHandler("help",    lambda u,c: payment_callback(
        type('obj', (object,), {'callback_query': type('q', (object,), {
            'answer': lambda: None, 'from_user': u.effective_user,
            'message': u.message, 'data': 'help'
        })()})(), c)
    ))
    app.add_handler(CallbackQueryHandler(payment_callback))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, convert_handler))

    print("🤖 FileConverter Bot ishga tushdi!")
    print("━" * 40)
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
