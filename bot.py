import hmac, hashlib, random, string, logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# === CONFIG ===
BOT_TOKEN = "8475934439:AAHlaKfYR3TUNserPFjSDRQPUXtJ9sXFH1M"  # <- Change this!
CHANNELS = [
    ("@studyverse_network_sv", "https://t.me/studyverse_network_sv"),
    ("@studyverse_network", "https://t.me/studyverse_network")
]
SECRET_KEY = "STUDYVERSE2025"
OWNER_LINK = "https://t.me/mr_bean_teddy_lover"
SITE_LINK = "https://studyverse-network.netlify.app/auth.html"

# === LOGGING ===
logging.basicConfig(level=logging.INFO)

# === TOKEN GENERATOR ===
def generate_token():
    now = datetime.now()
    base = now.strftime('%a').upper()[:3] + "-" + now.strftime('%d') + now.strftime('%b').upper()
    digest = hmac.new(SECRET_KEY.encode(), base.encode(), hashlib.sha256).hexdigest().upper()
    prefix = digest[:8]
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}/{suffix}"

# === START HANDLER ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    joined_all, _ = await check_all_channels(context, user_id)

    if joined_all:
        await send_token(update, context)
    else:
        keyboard = [[InlineKeyboardButton(f"📥 Join {name[1:]}", url=url)] for name, url in CHANNELS]
        keyboard.append([
            InlineKeyboardButton("✅ I Joined", callback_data="check"),
            InlineKeyboardButton("👑 Owner", url=OWNER_LINK)
        ])

        await update.message.reply_text(
            "<b>🚀 Welcome to StudyVerse Network!</b>\n\n"
            "📚 Free Educational Resources — Notes, PYQs, Live Batches, Test Series & more!\n\n"
            "🔐 Access is secured via channel membership.\n\n"
            "👉 Please join the below channels to unlock your daily access token 👇",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# === VERIFY BUTTON HANDLER ===
async def check_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    joined_all, not_joined = await check_all_channels(context, user_id)

    if joined_all:
        await query.edit_message_text("✅ Channels verified!\n⏳ Generating your access token...", parse_mode="HTML")
        await send_token(query, context, edit=True)
    else:
        not_joined_list = "\n".join([f"🔸 {ch[1:]}" for ch, _ in not_joined])
        keyboard = [
            [InlineKeyboardButton("🔁 Retry", callback_data="check")],
            [InlineKeyboardButton("👑 Owner Profile", url=OWNER_LINK)]
        ]

        await query.edit_message_text(
            f"❌ You still haven’t joined:\n\n<code>{not_joined_list}</code>\n\n"
            "📛 Access will be revoked if you leave any channel.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# === CHECK MEMBERSHIP ===
async def check_all_channels(context, user_id):
    not_joined = []
    for username, url in CHANNELS:
        try:
            member = await context.bot.get_chat_member(username, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                not_joined.append((username, url))
        except Exception as e:
            logging.warning(f"Error checking {username}: {e}")
            not_joined.append((username, url))
    return len(not_joined) == 0, not_joined

# === SEND TOKEN ===
async def send_token(obj, context, edit=False):
    token = generate_token()
    keyboard = [
        [InlineKeyboardButton("🔐 Access Website", url=SITE_LINK)],
        [InlineKeyboardButton("👑 Owner", url=OWNER_LINK)]
    ]
    text = (
        "<b>🎉 Access Granted!</b>\n\n"
        "Here is your <u>one-time token</u> for today:\n\n"
        f"<code>{token}</code>\n\n"
        "✅ Paste this on the website to continue!\n"
        "⚠️ Note: If you leave any channel later, your access will be revoked automatically."
    )

    if edit:
        await obj.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await obj.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

# === ERROR HANDLER ===
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Update error: {context.error}")

# === RUN THE BOT ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_channels, pattern="check"))
    app.add_error_handler(error_handler)
    print("🤖 Bot is live! @StudyVerseKey_bot")
    app.run_polling()

if __name__ == "__main__":
    main()
