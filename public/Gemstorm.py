import sqlite3
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError
import asyncio
import time

# Bot Token
TOKEN = "7735860907:AAF9jgG5DjmIZvbizRqxUkUj4yVPKp_xK_8"

# Channel and Group IDs
CHANNEL_ID = "@GemStorm_channel"
GROUP_ID = "@GemStorm_group"

# Database Setup
def init_db():
    print("Initializing database...")
    conn = sqlite3.connect("gemstorm.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    ton_balance REAL DEFAULT 0.0,
                    referrals INTEGER DEFAULT 0,
                    last_daily_reward INTEGER DEFAULT 0,
                    referred_by INTEGER
                 )''')
    conn.commit()
    conn.close()
    print("Database initialized.")

# Get User Data
def get_user(user_id):
    conn = sqlite3.connect("gemstorm.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

# Update User Data
def update_user(user_id, ton_balance=None, referrals=None, last_daily_reward=None, referred_by=None):
    conn = sqlite3.connect("gemstorm.db")
    c = conn.cursor()
    user = get_user(user_id)
    if not user:
        c.execute("INSERT INTO users (user_id, ton_balance, referrals, last_daily_reward, referred_by) VALUES (?, ?, ?, ?, ?)",
                  (user_id, 0.0, 0, 0, referred_by))
    else:
        if ton_balance is not None:
            c.execute("UPDATE users SET ton_balance = ? WHERE user_id = ?", (ton_balance, user_id))
        if referrals is not None:
            c.execute("UPDATE users SET referrals = ? WHERE user_id = ?", (referrals, user_id))
        if last_daily_reward is not None:
            c.execute("UPDATE users SET last_daily_reward = ? WHERE user_id = ?", (last_daily_reward, user_id))
        if referred_by is not None:
            c.execute("UPDATE users SET referred_by = ? WHERE user_id = ?", (referred_by, user_id))
    conn.commit()
    conn.close()

# Check Membership
async def check_membership(context: ContextTypes.DEFAULT_TYPE, user_id: int, chat_id: str) -> bool:
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramError as e:
        print(f"Membership check failed for user {user_id}: {e}")
        return False

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Start command received")
    user_id = update.effective_user.id
    args = context.args

    # Handle Referral
    referred_by = int(args[0]) if args and args[0].isdigit() and int(args[0]) != user_id else None
    if referred_by:
        user = get_user(user_id)
        if not user:  # New user
            update_user(user_id, referred_by=referred_by)
            referrer = get_user(referred_by)
            if referrer:
                new_referrals = referrer[2] + 1
                new_balance = referrer[1] + 0.5  # 0.5 TON per referral
                update_user(referred_by, ton_balance=new_balance, referrals=new_referrals)

    # Welcome Message
    welcome_message = (
        "Welcome to GemStorm! 🚀\n\n"
        "Join the exciting TON game! Collect TON, invite friends, and climb the leaderboard. 💎\n\n"
        "🔥 **How to Play:**\n"
        "- Join our channel and group to stay updated.\n"
        "- Invite friends using your referral link to earn 0.5 TON per referral.\n"
        "- Claim daily rewards (0.25 to 0.5 TON) to boost your balance.\n"
        "- Stay active in our community to unlock exclusive bonuses!\n\n"
        f"📢 **Join Us:**\n"
        f"- Channel: {CHANNEL_ID}\n"
        f"- Group: {GROUP_ID}\n\n"
        "Start now and build your TON empire! 💰"
    )

    # Glassy Interface
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/GemStorm_channel")],
        [InlineKeyboardButton("👥 Join Group", url=f"https://t.me/GemStorm_group")],
        [InlineKeyboardButton("🔗 Referral Link", callback_data="referral")],
        [InlineKeyboardButton("💰 Account Info", callback_data="account")],
        [InlineKeyboardButton("🎁 Daily Reward", callback_data="daily_reward")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="Markdown")
        print("Welcome message sent")
    except TelegramError as e:
        print(f"Failed to send welcome message: {e}")

# Button Handler
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    print(f"Button clicked: {data} by user {user_id}")

    # Verify Membership
    is_channel_member = await check_membership(context, user_id, CHANNEL_ID)
    is_group_member = await check_membership(context, user_id, GROUP_ID)

    if not (is_channel_member and is_group_member):
        user = get_user(user_id)
        if user and user[1] >= 0.5:
            new_balance = user[1] - 0.5
            update_user(user_id, ton_balance=new_balance)
            await query.message.reply_text("⚠️ Warning: You have left the channel or group. 0.5 TON has been deducted.")
        await query.message.reply_text(f"Please join both {CHANNEL_ID} and {GROUP_ID} to continue.")
        return

    if data == "referral":
        referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
        await query.message.reply_text(f"Your referral link: {referral_link}\nInvite friends to earn 0.5 TON per referral!")
    
    elif data == "account":
        user = get_user(user_id)
        balance = user[1] if user else 0.0
        referrals = user[2] if user else 0
        await query.message.reply_text(
            f"💰 **Your Account**\n"
            f"TON Balance: {balance:.2f} TON\n"
            f"Referrals: {referrals}",
            parse_mode="Markdown"
        )
    
    elif data == "daily_reward":
        user = get_user(user_id)
        current_time = int(time.time())
        one_day = 24 * 60 * 60

        if user and (current_time - user[3]) >= one_day:
            reward = random.uniform(0.25, 0.5)
            new_balance = user[1] + reward
            update_user(user_id, ton_balance=new_balance, last_daily_reward=current_time)
            await query.message.reply_text(f"🎉 You claimed {reward:.2f} TON as your daily reward!")
        else:
            await query.message.reply_text("⏳ You can claim your daily reward once every 24 hours.")

# Periodic Membership Check
async def check_membership_periodically(application: Application):
    print("Starting periodic membership check...")
    while True:
        conn = sqlite3.connect("gemstorm.db")
        c = conn.cursor()
        c.execute("SELECT user_id FROM users")
        users = c.fetchall()
        conn.close()

        for (user_id,) in users:
            is_channel_member = await check_membership(application, user_id, CHANNEL_ID)
            is_group_member = await check_membership(application, user_id, GROUP_ID)
            if not (is_channel_member and is_group_member):
                user = get_user(user_id)
                if user and user[1] >= 0.5:
                    new_balance = user[1] - 0.5
                    update_user(user_id, ton_balance=new_balance)
                    try:
                        await application.bot.send_message(user_id, "⚠️ Warning: You have left the channel or group. 0.5 TON has been deducted.")
                    except TelegramError as e:
                        print(f"Failed to send warning to user {user_id}: {e}")
        await asyncio.sleep(3600)  # Check every hour

def main():
    print("Main function started")
    init_db()
    try:
        application = Application.builder().token(TOKEN).build()
        print("Application built successfully")
    except Exception as e:
        print(f"Failed to build application: {e}")
        return

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Start Periodic Membership Check
    try:
        application.job_queue.run_once(check_membership_periodically, 0)
        print("Job queue started")
    except AttributeError as e:
        print(f"Job queue error: {e}")
        return

    print("Starting polling...")
    try:
        application.run_polling()
    except Exception as e:
        print(f"Polling error: {e}")

if __name__ == "__main__":
    print("Bot is starting...")
    main()
