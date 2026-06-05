from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import get_or_create_user, is_premium, get_today_usage

FREE_LIMIT = 3

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username or "")

    premium = is_premium(user.id)
    today = get_today_usage(user.id)

    if premium:
        status_line = "✨ <b>Premium</b> — cheksiz konversiya faol!"
    else:
        status_line = f"🆓 Bepul rejim — bugun {today}/{FREE_LIMIT} ta ishlatildi"

    text = (
        f"👋 Salom, <b>{user.first_name}</b>!\n\n"
        "🤖 <b>FileConverter Bot</b>ga xush kelibsiz —\n"
        "fayllarni bir formatdan ikkinchisiga\n"
        "⚡ <i>bir zumda</i> aylantiruvchi bot!\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "📂 <b>Nima qila olaman?</b>\n\n"
        "📄 PDF  →  Word (.docx)\n"
        "📝 Word  →  PDF\n"
        "🖼  Rasm  →  PDF\n"
        "📸 PDF  →  Rasm\n"
        "📊 Excel  →  PDF\n"
        "🔗 PDF birlashtirish\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Sizning holatiz: {status_line}\n\n"
        "📎 <b>Faylni shu yerga yuboring — men darhol ishlayman!</b>"
    )

    keyboard = []
    if not premium:
        keyboard.append([
            InlineKeyboardButton("⭐ Premium olish — 25 000 so'm/oy", callback_data="pay_info")
        ])
    keyboard.append([
        InlineKeyboardButton("📊 Statistika", callback_data="my_stats"),
        InlineKeyboardButton("❓ Yordam", callback_data="help")
    ])

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
