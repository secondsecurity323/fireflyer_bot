import os
import re
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatMemberStatus
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

BAD_WORDS = ['فحش1', 'فحش2', 'بدکلمه']
LINK_PATTERN = r"(https?://|t\.me/|telegram\.me/)"

ADMIN_USERNAME = "Secondsecurity"

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        await update.message.reply_text(f"خوش اومدی {user.first_name}! ❤️")

async def anti_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if re.search(LINK_PATTERN, update.message.text or ""):
        await update.message.delete()

async def anti_bad_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if any(word in update.message.text.lower() for word in BAD_WORDS):
        await update.message.delete()

async def no_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.forward_date:
        await update.message.delete()

async def user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    chat = update.effective_chat
    member = await chat.get_member(user.id)

    status_map = {
        ChatMemberStatus.OWNER: "مالک",
        ChatMemberStatus.ADMINISTRATOR: "ادمین",
        ChatMemberStatus.MEMBER: "عضو معمولی",
        ChatMemberStatus.RESTRICTED: "محدودشده",
        ChatMemberStatus.LEFT: "ترک‌کرده",
        ChatMemberStatus.KICKED: "اخراج‌شده"
    }

    msg = f"""🔍 مشخصات شما:
👤 نام: {user.full_name}
🏷 یوزرنیم: @{user.username if user.username else 'ندارد'}
💼 مقام: {status_map.get(member.status, 'نامشخص')}
"""
    await update.message.reply_text(msg)

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.username == ADMIN_USERNAME:
        if update.message.reply_to_message:
            target = update.message.reply_to_message.from_user
            await update.effective_chat.promote_member(
                user_id=target.id,
                can_manage_chat=True,
                can_delete_messages=True,
                can_promote_members=False,
                can_change_info=False,
                can_invite_users=True
            )
            await update.message.reply_text(f"✅ {target.full_name} ادمین شد.")
        else:
            await update.message.reply_text("روی پیام کسی ریپلای کن تا ادمینش کنم.")
    else:
        await update.message.reply_text("⛔ فقط سازنده‌ی ربات می‌تونه این کارو انجام بده.")

# ساخت اپلیکیشن و ثبت هندلرها
application = ApplicationBuilder().token(BOT_TOKEN).build()

application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
application.add_handler(MessageHandler(filters.Regex(LINK_PATTERN), anti_link))
application.add_handler(MessageHandler(filters.Regex("|".join(BAD_WORDS)), anti_bad_words))
application.add_handler(MessageHandler(filters.FORWARDED, no_forward))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_info))
application.add_handler(CommandHandler("addadmin", add_admin))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "Fire Flyer Bot is alive 🚀"

if __name__ == "__main__":
    app.run(port=8080)
