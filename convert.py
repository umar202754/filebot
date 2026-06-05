import os
import tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import get_or_create_user, is_premium, get_today_usage, log_usage
from services.converter import detect_conversion, run_conversion

FREE_LIMIT = 3
MAX_FREE_MB = 5
MAX_PREMIUM_MB = 50

CONV_EMOJI = {
    "pdf_to_docx":  ("📄", "PDF → Word"),
    "docx_to_pdf":  ("📝", "Word → PDF"),
    "image_to_pdf": ("🖼",  "Rasm → PDF"),
    "pdf_to_image": ("📸", "PDF → Rasm"),
    "excel_to_pdf": ("📊", "Excel → PDF"),
}

async def convert_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username or "")

    premium = is_premium(user.id)
    today_count = get_today_usage(user.id)

    # Limit tekshirish
    if not premium and today_count >= FREE_LIMIT:
        keyboard = [[InlineKeyboardButton("⭐ Premium olish — cheksiz!", callback_data="pay_info")]]
        await update.message.reply_text(
            "⛔ <b>Kunlik limit tugadi!</b>\n\n"
            f"🆓 Bepul rejimda kuniga <b>{FREE_LIMIT} ta</b> konversiya.\n\n"
            "⭐ <b>Premium</b> oling va:\n"
            "  ✅ Cheksiz konversiya\n"
            "  ✅ 50 MB gacha fayllar\n"
            "  ✅ Ustuvor navbat\n\n"
            "💰 Atigi <b>25 000 so'm/oy</b>!",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    msg = update.message
    file_obj = None
    filename = ""
    mime_type = ""

    if msg.document:
        file_obj = msg.document
        filename = file_obj.file_name or "file"
        mime_type = file_obj.mime_type or ""
    elif msg.photo:
        file_obj = msg.photo[-1]
        filename = "photo.jpg"
        mime_type = "image/jpeg"

    if not file_obj:
        await msg.reply_text("❌ Fayl topilmadi. Iltimos qaytadan yuboring.")
        return

    file_size_mb = file_obj.file_size / (1024 * 1024)
    max_mb = MAX_PREMIUM_MB if premium else MAX_FREE_MB

    if file_size_mb > max_mb:
        tip = "" if premium else "\n\n⭐ <b>Premium</b> oling — 50 MB gacha!"
        await msg.reply_text(
            f"📦 <b>Fayl hajmi katta!</b>\n\n"
            f"📁 Fayl hajmi: <b>{file_size_mb:.1f} MB</b>\n"
            f"🚫 Limit: <b>{max_mb} MB</b>{tip}",
            parse_mode="HTML"
        )
        return

    conv_type = detect_conversion(filename, mime_type)
    if not conv_type:
        await msg.reply_text(
            "🤔 <b>Bu format qo'llab-quvvatlanmaydi.</b>\n\n"
            "✅ Qo'llab-quvvatlanadigan formatlar:\n"
            "  📄 PDF\n"
            "  📝 DOCX, DOC\n"
            "  🖼 JPG, PNG, WEBP\n"
            "  📊 XLSX, XLS\n\n"
            "Shu formatlarda fayl yuboring!",
            parse_mode="HTML"
        )
        return

    emoji, label = CONV_EMOJI.get(conv_type, ("🔄", conv_type))

    # Progress xabari
    wait_msg = await msg.reply_text(
        f"⏳ <b>Jarayon boshlandi...</b>\n\n"
        f"{emoji} {label}\n"
        f"📁 Fayl: {filename}\n"
        f"📦 Hajm: {file_size_mb:.1f} MB\n\n"
        "🔄 Iltimos kuting...",
        parse_mode="HTML"
    )

    try:
        tmp_dir = tempfile.mkdtemp()
        input_path = os.path.join(tmp_dir, filename)

        await wait_msg.edit_text(
            f"⬇️ <b>Fayl yuklanmoqda...</b>\n\n"
            f"{emoji} {label}\n"
            "▓▓▓░░░░░░░ 30%",
            parse_mode="HTML"
        )

        tg_file = await file_obj.get_file()
        await tg_file.download_to_drive(input_path)

        await wait_msg.edit_text(
            f"⚙️ <b>Konvertatsiya qilinmoqda...</b>\n\n"
            f"{emoji} {label}\n"
            "▓▓▓▓▓▓░░░░ 60%",
            parse_mode="HTML"
        )

        output_path = run_conversion(conv_type, input_path)

        await wait_msg.edit_text(
            f"📤 <b>Yuborilmoqda...</b>\n\n"
            f"{emoji} {label}\n"
            "▓▓▓▓▓▓▓▓▓░ 90%",
            parse_mode="HTML"
        )

        out_filename = os.path.basename(output_path)
        remaining = FREE_LIMIT - (today_count + 1)

        if premium:
            footer = "✨ Premium | Cheksiz konversiya"
        else:
            footer = f"🆓 Bugun qoldi: {remaining}/{FREE_LIMIT} ta"

        with open(output_path, "rb") as f:
            await msg.reply_document(
                document=f,
                filename=out_filename,
                caption=(
                    f"✅ <b>Tayyor!</b>\n\n"
                    f"{emoji} {label}\n"
                    f"📁 {out_filename}\n\n"
                    f"{footer}"
                ),
                parse_mode="HTML"
            )

        await wait_msg.delete()
        log_usage(user.id, conv_type)

        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        await wait_msg.edit_text(
            "❌ <b>Xatolik yuz berdi!</b>\n\n"
            "Faylni qaytadan yuboring yoki boshqa format sinab ko'ring.\n\n"
            f"🔧 Xato: <code>{str(e)[:120]}</code>",
            parse_mode="HTML"
        )
