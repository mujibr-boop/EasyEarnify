import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ================= CONFIG =================
BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"  # Railway env ya direct paste
MIN_WITHDRAW = 500
TASK_REWARD = 50

# ================= DATA (TEMP) =================
users = {}  # user_id: {balance, referrals, tasks_done}

# ================= LOGGING =================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================= HELPERS =================
def get_user(uid):
    if uid not in users:
        users[uid] = {
            "balance": 0,
            "referrals": 0,
            "tasks_done": []
        }
    return users[uid]

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    data = get_user(uid)

    # referral handling
    if context.args:
        ref_id = int(context.args[0])
        if ref_id != uid and ref_id in users:
            users[ref_id]["referrals"] += 1

    keyboard = [
        [InlineKeyboardButton("📝 Task Work", callback_data="tasks")],
        [InlineKeyboardButton("💰 Earnings", callback_data="earnings")],
        [InlineKeyboardButton("👥 Refer & Earn", callback_data="refer")],
        [InlineKeyboardButton("🏦 Withdraw", callback_data="withdraw")]
    ]

    await update.message.reply_text(
        "Welcome 👋\n\nChoose an option below:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= CALLBACKS =================
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    data = get_user(uid)

    if query.data == "tasks":
        buttons = [
            [InlineKeyboardButton("Task 1", callback_data="task_1")],
            [InlineKeyboardButton("Task 2", callback_data="task_2")],
            [InlineKeyboardButton("Task 3", callback_data="task_3")],
            [InlineKeyboardButton("Task 4", callback_data="task_4")],
            [InlineKeyboardButton("Task 5", callback_data="task_5")]
        ]
        await query.edit_message_text(
            "Select a task 👇",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif query.data.startswith("task_"):
        task_no = query.data.split("_")[1]

        await query.edit_message_text(
            f"🔗 Task {task_no}\n\n"
            "Complete the task.\n\n"
            "⚠️ Admin ke paas complete data hota hai.\n"
            "Cheating ki toh pakde jaoge.\n\n"
            "Have you completed the task?",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ YES", callback_data=f"done_{task_no}"),
                    InlineKeyboardButton("❌ NO", callback_data="tasks")
                ]
            ])
        )

    elif query.data.startswith("done_"):
        task_no = query.data.split("_")[1]

        if task_no not in data["tasks_done"]:
            data["tasks_done"].append(task_no)
            data["balance"] += TASK_REWARD

        await query.edit_message_text(
            "✅ Task marked as completed.\n\n"
            "👉 Proceed karne ke liye **1 new member refer karo**.\n\n"
            "Admin verification ke baad reward final hoga."
        )

    elif query.data == "earnings":
        await query.edit_message_text(
            f"💰 Your Earnings\n\n"
            f"Balance: {data['balance']}\n"
            f"Referrals: {data['referrals']}"
        )

    elif query.data == "refer":
        link = f"https://t.me/{context.bot.username}?start={uid}"
        await query.edit_message_text(
            f"👥 Refer & Earn\n\n"
            f"Your referral link 👇\n{link}\n\n"
            "Invite friends to unlock next tasks."
        )

    elif query.data == "withdraw":
        if data["balance"] < MIN_WITHDRAW:
            await query.edit_message_text(
                f"❌ Withdraw not available\n\n"
                f"Minimum payout: {MIN_WITHDRAW}\n"
                f"Your balance: {data['balance']}"
            )
        else:
            await query.edit_message_text(
                "✅ Withdraw request received.\n\n"
                "Admin will review and approve manually."
            )

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
