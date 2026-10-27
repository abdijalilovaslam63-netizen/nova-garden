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
        [InlineKeyboardButton("🌳 Daraxtlar", callback_data="trees"),
         InlineKeyboardButton("🌷 Gullar", callback_data="flowers")],
        [InlineKeyboardButton("🍃 Barglarim", callback_data="leaves"),
         InlineKeyboardButton("👥 Referal", callback_data="referral")],
        [InlineKeyboardButton("🌳 Shaxsiy bog‘im", callback_data="garden")],
        [InlineKeyboardButton("🎮 3D bog‘", web_app=WebAppInfo(url="https://abdijalilovaslam63-netizen.github.io/nova-garden/"))],
        [InlineKeyboardButton("💧 Daraxtni parvarishlash", callback_data="care")],
        [InlineKeyboardButton("⏱ Kunlik vazifa", callback_data="daily")],
        [InlineKeyboardButton("📱 Ijtimoiy vazifalar", callback_data="social")],
        [InlineKeyboardButton("📺 Reklama ko‘rish", callback_data="ads")],
        [InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check")]
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
        "🌱 NOVA Garden botiga xush kelibsiz!\n\n"
        "Virtual bog‘ingizni yarating va tabiatga hissa qo‘shing.\n"
        "Botdan foydalanish uchun NOVA kanaliga obuna bo‘ling.",
        reply_markup=menu()
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = str(query.from_user.id)
    users = load_users()

    if query.data == "check":
        try:
            member = await context.bot.get_chat_member(CHANNEL, int(uid))
            if member.status in ("member", "administrator", "creator"):
                await query.message.reply_text(
                    "✅ Kanalga obunangiz tasdiqlandi!\n"
                    "NOVA bog‘ingizga xush kelibsiz.",
                    reply_markup=menu()
                )
            else:
                await query.message.reply_text(
                    "❌ Avval @Nova_Garden kanaliga obuna bo‘ling."
                )
        except Exception:
            await query.message.reply_text(
                "Obunani tekshirib bo‘lmadi. Bot kanalda admin ekanini tekshiring."
            )

    elif query.data == "trees":
        keyboard = [
            [InlineKeyboardButton("🍎 Olma", callback_data="plant_olma"),
             InlineKeyboardButton("🍑 O‘rik", callback_data="plant_orik")],
            [InlineKeyboardButton("🍐 Nok", callback_data="plant_nok"),
             InlineKeyboardButton("🍒 Olcha", callback_data="plant_olcha")],
            [InlineKeyboardButton("🌲 Qarag‘ay", callback_data="plant_qaragay"),
             InlineKeyboardButton("🌿 Archa", callback_data="plant_archa")],
            [InlineKeyboardButton("🌳 Eman", callback_data="plant_eman"),
             InlineKeyboardButton("🍁 Chinor", callback_data="plant_chinor")],
        ]
        await query.message.reply_text(
            "🌳 Bog‘ingizga ekish uchun daraxtni tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


    elif query.data.startswith("plant_"):
        tree_names = {
            "plant_olma": "Olma",
            "plant_orik": "O‘rik",
            "plant_nok": "Nok",
            "plant_olcha": "Olcha",
            "plant_qaragay": "Qarag‘ay",
            "plant_archa": "Archa",
            "plant_eman": "Eman",
            "plant_chinor": "Chinor",
        }
        tree = tree_names.get(query.data)
        if not tree:
            await query.message.reply_text("Bu daraxt topilmadi.")
        else:
            user_data = users.setdefault(uid, {
                "name": query.from_user.first_name,
                "leaves": 0,
                "trees": [],
                "flowers": [],
                "invited_by": None,
            })
            user_data.setdefault("trees", []).append({
                "name": tree,
                "stage": "Nihol",
                "growth": 0,
                "planted_at": datetime.now(timezone.utc).isoformat(),
                "care_bonus": 0,
            })
            save_users(users)
            await query.message.reply_text(
                f"🌱 {tree} daraxti shaxsiy bog‘ingizga ekildi!\n"
                "Hozirgi bosqich: Nihol.\n"
                "Daraxt parvarishi keyingi bosqichda qo‘shiladi."
            )

    elif query.data == "care":
        trees = users.get(uid, {}).get("trees", [])
        if not trees:
            await query.message.reply_text("🌱 Avval Daraxtlar bo‘limidan daraxt eking.")
        else:
            keyboard = [
                [InlineKeyboardButton(
                    f"🌳 {tree.get('name', 'Daraxt')} ({tree.get('growth', 0)}%)",
                    callback_data=f"caretree_{i}"
                )]
                for i, tree in enumerate(trees)
            ]
            await query.message.reply_text(
                "💧 Qaysi daraxtni parvarishlaysiz?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    elif query.data.startswith("caretree_"):
        try:
            i = int(query.data.split("_", 1)[1])
            trees = users.get(uid, {}).get("trees", [])
            if i < 0 or i >= len(trees):
                raise ValueError
            tree = trees[i]
            keyboard = [[
                InlineKeyboardButton("💧 Suv — 5 barg", callback_data=f"water_{i}"),
                InlineKeyboardButton("🌿 O‘g‘it — 10 barg", callback_data=f"fertilizer_{i}")
            ]]
            await query.message.reply_text(
                f"🌳 {tree.get('name', 'Daraxt')} parvarishi\n"
                f"🍃 Barglaringiz: {users[uid].get('leaves', 0)}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except (ValueError, IndexError):
            await query.message.reply_text("Daraxt tanlashda xatolik. Qayta urinib ko‘ring.")

    elif query.data.startswith(("water_", "fertilizer_")):
        try:
            action, index_text = query.data.split("_", 1)
            i = int(index_text)
            user_data = users.get(uid, {})
            trees = user_data.get("trees", [])
            if i < 0 or i >= len(trees):
                raise ValueError

            cost = 5 if action == "water" else 10
            if user_data.get("leaves", 0) < cost:
                await query.message.reply_text(
                    f"🍃 Barg yetarli emas. Bu amal uchun {cost} barg kerak."
                )
            else:
                tree = trees[i]
                tree.setdefault("planted_at", datetime.now(timezone.utc).isoformat())
                tree.setdefault("care_bonus", 0)
                tree["care_bonus"] = min(5, tree["care_bonus"] + (1 if action == "water" else 2))
                user_data["leaves"] -= cost

                planted = datetime.fromisoformat(tree["planted_at"])
                elapsed = max(0, (datetime.now(timezone.utc) - planted).total_seconds())
                tree["growth"] = min(100, int(elapsed / (7 * 24 * 60 * 60) * 95) + tree["care_bonus"])

                if tree["growth"] >= 100:
                    tree["stage"] = "Hosilga kirgan"
                elif tree["growth"] >= 60:
                    tree["stage"] = "Yosh daraxt"
                elif tree["growth"] >= 30:
                    tree["stage"] = "Yosh nihol"
                else:
                    tree["stage"] = "Nihol"
                save_users(users)
                item = "Suv" if action == "water" else "O‘g‘it"
                await query.message.reply_text(
                    f"✅ {tree.get('name', 'Daraxt')} daraxtiga {item.lower()} berildi!\n"
                    f"🌱 O‘sishi: {tree['growth']}%\n"
                    f"🍃 Qolgan barglar: {user_data['leaves']}"
                )
        except (ValueError, IndexError):
            await query.message.reply_text("Xatolik yuz berdi. Qayta urinib ko‘ring.")

    elif query.data == "flowers":
        await query.message.reply_text(
            "🌷 Gullar:\n🌹 Atirgul\n💜 Siren\n\n"
            "Gul ekish funksiyasi keyingi bosqichda qo‘shiladi."
        )

    elif query.data == "garden":
        trees = users.get(uid, {}).get("trees", [])
        if not trees:
            await query.message.reply_text(
                "🌱 Bog‘ingiz hozircha bo‘sh. Daraxtlar bo‘limidan birinchi daraxtingizni eking."
            )
        else:
            now = datetime.now(timezone.utc)
            lines = ["🌳 Sizning shaxsiy bog‘ingiz:", ""]
            for i, tree in enumerate(trees, 1):
                try:
                    planted = datetime.fromisoformat(
                        tree.get("planted_at", now.isoformat())
                    )
                    if planted.tzinfo is None:
                        planted = planted.replace(tzinfo=timezone.utc)
                    elapsed = max(0, (now - planted).total_seconds())
                    growth = min(
                        100,
                        int(elapsed / (7 * 24 * 60 * 60) * 95)
                        + tree.get("care_bonus", 0)
                    )
                    tree["growth"] = growth
                    if growth >= 100:
                        tree["stage"] = "Hosilga kirgan"
                    elif growth >= 60:
                        tree["stage"] = "Yosh daraxt"
                    elif growth >= 30:
                        tree["stage"] = "Yosh nihol"
                    else:
                        tree["stage"] = "Nihol"
                except (ValueError, TypeError):
                    pass
                lines.append(
                    f"{i}. 🌳 {tree.get('name', 'Daraxt')} — "
                    f"{tree.get('stage', 'Nihol')} "
                    f"({tree.get('growth', 0)}% o‘sish)"
                )
            save_users(users)
            await query.message.reply_text("\n".join(lines))

    elif query.data == "daily":
        from datetime import timedelta
        user_data = users.setdefault(uid, {
            "name": query.from_user.first_name,
            "leaves": 0,
            "trees": [],
            "flowers": [],
            "invited_by": None,
        })
        now = datetime.now(timezone(timedelta(hours=5)))
        today = now.strftime("%Y-%m-%d")
        if user_data.get("daily_claim_date") == today:
            await query.message.reply_text("✅ Bugungi kunlik vazifani allaqachon bajargansiz. Ertaga qayting!")
        else:
            started = user_data.get("daily_start_date")
            if started != today:
                user_data["daily_start_date"] = today
                user_data["daily_start_time"] = now.timestamp()
                save_users(users)
                await query.message.reply_text(
                    "⏱ Kunlik vazifa boshlandi! Botdan 10 daqiqa davomida foydalaning, "
                    "so‘ng shu tugmani yana bosing. Mukofot: 30 barg."
                )
            else:
                elapsed = now.timestamp() - user_data.get("daily_start_time", now.timestamp())
                if elapsed < 600:
                    remaining = int(600 - elapsed)
                    minutes = remaining // 60
                    seconds = remaining % 60
                    await query.message.reply_text(
                        f"⏳ Yana {minutes} daqiqa {seconds} soniya kuting, keyin qayta bosing."
                    )
                else:
                    user_data["leaves"] = user_data.get("leaves", 0) + 30
                    user_data["daily_claim_date"] = today
                    save_users(users)
                    await query.message.reply_text(
                        f"🎉 Kunlik vazifa bajarildi! +30 barg. Jami: {user_data['leaves']} barg."
                    )

    elif query.data == "social":
        keyboard = [
            [InlineKeyboardButton("📢 Telegram", url="https://t.me/Nova_Garden"),
             InlineKeyboardButton("📸 Instagram", url="https://instagram.com/")],
            [InlineKeyboardButton("▶️ YouTube", url="https://www.youtube.com/@NovaGardenuz")],
            [InlineKeyboardButton("🎁 Mukofotni tekshirish", callback_data="social_claim")]
        ]
        await query.message.reply_text(
            "📱 Ijtimoiy vazifalar\n\n"
            "1. Telegram, Instagram va YouTube sahifalarimizga obuna bo‘ling.\n"
            "2. Har bir vazifa uchun 50 barg olish mumkin.\n"
            "Eslatma: hozircha mukofot obunani avtomatik tasdiqlamaydi.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "social_claim":
        user_data = users.setdefault(uid, {
            "name": query.from_user.first_name,
            "leaves": 0,
            "trees": [],
            "flowers": [],
            "invited_by": None,
        })
        completed = user_data.setdefault("social_claimed", [])
        keyboard = []
        for task, label in [
            ("telegram", "Telegram"),
            ("instagram", "Instagram"),
            ("youtube", "YouTube"),
        ]:
            if task in completed:
                keyboard.append([InlineKeyboardButton(f"✅ {label} — olindi", callback_data="social_claim")])
            else:
                keyboard.append([InlineKeyboardButton(f"🎁 {label} uchun 50 barg", callback_data=f"claim_{task}")])
        await query.message.reply_text(
            "🎁 Vazifani tanlang. Mukofot hozircha obuna avtomatik tekshirilmasdan beriladi.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("claim_"):
        task = query.data.split("_", 1)[1]
        if task not in ("telegram", "instagram", "youtube"):
            await query.message.reply_text("Noma’lum vazifa.")
        else:
            user_data = users.setdefault(uid, {
                "name": query.from_user.first_name,
                "leaves": 0,
                "trees": [],
                "flowers": [],
                "invited_by": None,
            })
            completed = user_data.setdefault("social_claimed", [])
            if task in completed:
                await query.message.reply_text("Bu vazifa mukofotini avval olgansiz.")
            else:
                completed.append(task)
                user_data["leaves"] = user_data.get("leaves", 0) + 50
                save_users(users)
                await query.message.reply_text(
                    f"🎉 +50 barg! Jami barglaringiz: {user_data['leaves']}."
                )

    elif query.data == "ads":
        from datetime import timedelta
        user_data = users.setdefault(uid, {
            "name": query.from_user.first_name,
            "leaves": 0,
            "trees": [],
            "flowers": [],
            "invited_by": None,
        })
        today = datetime.now(timezone(timedelta(hours=5))).strftime("%Y-%m-%d")
        if user_data.get("ads_date") != today:
            user_data["ads_date"] = today
            user_data["ads_count"] = 0
            save_users(users)

        count = user_data.get("ads_count", 0)
        if count >= 3:
            await query.message.reply_text("📺 Bugungi 3 ta reklama imkoniyatidan foydalandingiz. Ertaga qayting!")
        else:
            keyboard = [[InlineKeyboardButton("▶️ Sinov reklamasini ko‘rish (+20 barg)", callback_data="watch_ad")]]
            await query.message.reply_text(
                f"📺 Reklama sinov rejimi\n"
                f"🎁 Har bir reklama: 20 barg\n"
                f"📊 Bugun: {count}/3 ta\n\n"
                "Bu sinov tugmasi haqiqiy reklama ko‘rsatmaydi.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    elif query.data == "watch_ad":
        from datetime import timedelta
        user_data = users.setdefault(uid, {
            "name": query.from_user.first_name,
            "leaves": 0,
            "trees": [],
            "flowers": [],
            "invited_by": None,
        })
        today = datetime.now(timezone(timedelta(hours=5))).strftime("%Y-%m-%d")
        if user_data.get("ads_date") != today:
            user_data["ads_date"] = today
            user_data["ads_count"] = 0

        count = user_data.get("ads_count", 0)
        if count >= 3:
            await query.message.reply_text("📺 Bugungi limit tugadi. Ertaga qayting!")
        else:
            user_data["ads_count"] = count + 1
            user_data["leaves"] = user_data.get("leaves", 0) + 20
            save_users(users)
            await query.message.reply_text(
                f"🎁 Sinov mukofoti: +20 barg!\n"
                f"📺 Bugun: {user_data['ads_count']}/3 ta\n"
                f"🍃 Jami barglaringiz: {user_data['leaves']}"
            )

    elif query.data == "leaves":
        leaves = users.get(uid, {}).get("leaves", 0)
        await query.message.reply_text(f"🍃 Sizda {leaves} ta barg bor.")

    elif query.data == "referral":
        me = await context.bot.get_me()
        link = f"https://t.me/{me.username}?start=ref_{uid}"
        referrals = users.get(uid, {}).get("referrals", [])
        await query.message.reply_text(
            "👥 Do‘stlaringizni NOVA’ga taklif qiling!\n\n"
            f"🔗 Sizning havolangiz:\n{link}\n\n"
            f"👤 Taklif qilgan do‘stlaringiz: {len(referrals)} ta\n"
            f"🍃 Har bir yangi do‘st uchun: 50 barg\n"
            f"🎁 Jami referal mukofoti: {len(referrals) * 50} barg"
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
