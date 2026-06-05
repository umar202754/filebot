import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import is_premium, activate_premium, get_today_usage

PAYME_MERCHANT_ID = os.getenv("PAYME_MERCHANT_ID", "")
CLICK_SERVICE_ID  = os.getenv("CLICK_SERVICE_ID", "")
CLICK_MERCHANT_ID = os.getenv("CLICK_MERCHANT_ID", "")
ADMIN_ID          = os.getenv("ADMIN_ID", "")

PREMIUM_PRICE = 25000
PREMIUM_DAYS  = 30

async def premium_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user if update.message else update.callback_query.from_user
    premium = is_premium(user.id)

    if premium:
        msg_func = update.message.reply_text if update.message else update.callback_query.message.reply_text
        await msg_func(
            "⭐ <b>Siz Premium foydalanuvchisiz!</b>\n\n"
            "✅ Cheksiz konversiya\n"
            "✅ 50 MB gacha fayllar\n"
            "✅ Ustuvor navbat\n\n"
            "🙏 Botdan foydalanganingiz uchun rahmat!",
            parse_mode="HTML"
        )
        return

    keyboard = [
        [InlineKeyboardButton("💳 Payme orqali to'lash", callback_data="pay_payme")],
        [InlineKeyboardButton("💳 Click orqali to'lash",  callback_data="pay_click")],
        [InlineKeyboardButton("👨‍💼 Admin bilan bog'lanish", url="https://t.me/your_support")],
    ]

    text = (
        "⭐ <b>Premium obuna</b>\n\n"
        "🆓 Bepul vs ⭐ Premium:\n\n"
        "  Konversiya:  3 ta/kun  →  ♾ cheksiz\n"
        "  Fayl hajmi:  5 MB      →  50 MB\n"
        "  Navbat:      Oddiy     →  ⚡ Ustuvor\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Narxi: <b>{PREMIUM_PRICE:,} so'm/oy</b>\n"
        f"📅 Muddat: {PREMIUM_DAYS} kun\n\n"
        "👇 To'lov usulini tanlang:"
    )

    msg_func = update.message.reply_text if update.message else update.callback_query.message.reply_text
    await msg_func(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))


async def payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    if data == "pay_info":
        await premium_handler(update, context)

    elif data == "pay_payme":
        if not PAYME_MERCHANT_ID:
            await query.message.reply_text(
                "⚠️ <b>Payme hali sozlanmagan</b>\n\n"
                "👨‍💼 Admin bilan bog'laning: @your_support",
                parse_mode="HTML"
            )
            return
        url = (
            f"https://checkout.paycom.uz/{PAYME_MERCHANT_ID}"
            f"?amount={PREMIUM_PRICE * 100}&account[user_id]={user.id}"
        )
        keyboard = [[InlineKeyboardButton("💳 Payme'da to'lash →", url=url)]]
        await query.message.reply_text(
            "💳 <b>Payme orqali to'lash</b>\n\n"
            f"💰 Summa: <b>{PREMIUM_PRICE:,} so'm</b>\n"
            f"👤 Foydalanuvchi ID: <code>{user.id}</code>\n\n"
            "✅ To'lovdan so'ng Premium <b>avtomatik</b> faollashadi!\n\n"
            "👇 Tugmani bosing:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "pay_click":
        if not CLICK_SERVICE_ID:
            await query.message.reply_text(
                "⚠️ <b>Click hali sozlanmagan</b>\n\n"
                "👨‍💼 Admin bilan bog'laning: @your_support",
                parse_mode="HTML"
            )
            return
        url = (
            f"https://my.click.uz/services/pay"
            f"?service_id={CLICK_SERVICE_ID}"
            f"&merchant_id={CLICK_MERCHANT_ID}"
            f"&amount={PREMIUM_PRICE}"
            f"&transaction_param={user.id}"
        )
        keyboard = [[InlineKeyboardButton("💳 Click'da to'lash →", url=url)]]
        await query.message.reply_text(
            "💳 <b>Click orqali to'lash</b>\n\n"
            f"💰 Summa: <b>{PREMIUM_PRICE:,} so'm</b>\n"
            f"👤 Foydalanuvchi ID: <code>{user.id}</code>\n\n"
            "✅ To'lovdan so'ng Premium <b>avtomatik</b> faollashadi!\n\n"
            "👇 Tugmani bosing:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "my_stats":
        today = get_today_usage(user.id)
        premium = is_premium(user.id)
        await query.message.reply_text(
            f"📊 <b>Sizning statistikangiz</b>\n\n"
            f"👤 Ism: {user.first_name}\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"⭐ Holat: {'Premium ✨' if premium else 'Bepul 🆓'}\n"
            f"📁 Bugun: {today} ta konversiya\n",
            parse_mode="HTML"
        )

    elif data == "help":
        await query.message.reply_text(
            "❓ <b>Yordam</b>\n\n"
            "📎 Faylni yuboring — men o'zim formatni aniqlayman!\n\n"
            "📋 <b>Qo'llab-quvvatlanadigan formatlar:</b>\n"
            "  📄 PDF → Word\n"
            "  📝 Word → PDF\n"
            "  🖼 Rasm → PDF\n"
            "  📸 PDF → Rasm\n"
            "  📊 Excel → PDF\n\n"
            "🆓 Bepul: kuniga 3 ta, 5 MB gacha\n"
            "⭐ Premium: cheksiz, 50 MB gacha\n\n"
            "❗ Muammo bo'lsa: @your_support",
            parse_mode="HTML"
        )


async def activate_user_premium(user_id: int, context):
    activate_premium(user_id, days=PREMIUM_DAYS)
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🎉 <b>Premium faollashtirildi!</b>\n\n"
                "✅ Cheksiz konversiya\n"
                "✅ 50 MB gacha fayllar\n"
                "✅ Ustuvor navbat\n\n"
                "🙏 Xarid qilganingiz uchun rahmat!\n"
                "📎 Faylni yuboring — men tayorman!"
            ),
            parse_mode="HTML"
        )
    except Exception:
        pass
