import os
import json
import logging
from datetime import datetime, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("NOVA_BOT_TOKEN")
CHANNEL = "@Nova_Garden"
DATA_FILE = "users.json"

logging.basicConfig(level=logging.INFO)


def load_users():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "🎮 NOVA Mini App",
            web_app=WebAppInfo(
                url="https://abdijalilovaslam63-netizen.github.io/nova-garden/"
            )
        )]
    ])


def subscription_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "📢 NOVA kanaliga obuna bo‘lish",
            url="https://t.me/Nova_Garden"
        )],
        [InlineKeyboardButton(
            "✅ Obunani tekshirish",
            callback_data="check"
        )]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users = load_users()
    uid = str(user.id)

    if uid not in users:
        users[uid] = {
            "name": user.first_name,
            "leaves": 0,
            "trees": [],
            "flowers": [],
            "invited_by": None
        }

        if context.args and context.args[0].startswith("ref_"):
            ref_id = context.args[0][4:]
            if ref_id != uid and ref_id in users:
                invited = users[ref_id].setdefault("referrals", [])
                if uid not in invited:
                    users[uid]["invited_by"] = ref_id
                    invited.append(uid)
                    users[ref_id]["leaves"] = users[ref_id].get("leaves", 0) + 50

        save_users(users)

    await update.message.reply_text(
        "🌱 Assalomu alaykum! NOVA Garden loyihasiga xush kelibsiz!\n\n"
        "Davom etish uchun NOVA Telegram kanaliga obuna bo‘ling "
        "va obunani tasdiqlang.",
        reply_markup=subscription_menu()
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check":
        try:
            member = await context.bot.get_chat_member(
                CHANNEL, query.from_user.id
            )

            if member.status in ("member", "administrator", "creator"):
                await query.message.reply_text(
                    "✅ Kanalga obunangiz tasdiqlandi!\n\n"
                    "NOVA Mini App'ga xush kelibsiz! 🌱",
                    reply_markup=menu()
                )
            else:
                await query.message.reply_text(
                    "❌ Siz hali NOVA kanaliga obuna bo‘lmagansiz.",
                    reply_markup=subscription_menu()
                )

        except Exception:
            logging.exception("Obunani tekshirishda xatolik")
            await query.message.reply_text(
                "⚠️ Obunani tekshirib bo‘lmadi. "
                "Bot kanal admini ekanini tekshiring.",
                reply_markup=subscription_menu()
            )

def main():
    if not TOKEN:
        raise RuntimeError(
            "NOVA_BOT_TOKEN topilmadi. Tokenni xavfsiz sozlang."
        )

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    print("NOVA bot ishga tushmoqda...")
    app.run_polling()


if __name__ == "__main__":
    main()
