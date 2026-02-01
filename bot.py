import os
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

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ---- In-memory storage (simple, Railway safe for demo) ----
users = {}

MAX_TASKS = 5
MIN_WITHDRAW = 100  # example

TASK_TEXTS = {
    1: "🔹 *Task 1*\nVisit our partner and read carefully.\n[Click here to open task](https://example.com/task1)",
    2: "🔹 *Task 2*\nWatch the content fully.\n[Click here to open task](https://example.com/task2)",
    3: "🔹 *Task 3*\nFollow the instructions.\n[Click here to open task](https://example.com/task3)",
    4: "🔹 *Task 4*\nComplete the given action.\n[Click here to open task](https://example.com/task4)",
    5: "🔹 *Task 5*\nFinal task for today.\n[Click here to open task](https://example.com/task5)",
}

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id

    if uid not in users:
        users[uid] = {
            "tasks_done": 0,
            "balance": 0,
            "referrals": 0,
            "referrer": None
        }

        if context.args:
            try:
                ref_id = int(context.args[0])
                if ref_id != uid:
                    users[uid]["referrer"] = ref_id
                    if ref_id in users:
                        users[ref_id]["balance"] += int(0.10 * users[uid]["balance"])
            except:
                pass

    keyboard = [
        [InlineKeyboardButton("🧑‍💻 Task Work", callback_data="tasks")],
        [
            InlineKeyboardButton("💰 Withdraw", callback_data="withdraw"),
            InlineKeyboardButton("👥 Refer & Earn", callback_data="refer")
        ],
        [InlineKeyboardButton("⚠️ Warning", callback_data="warning")]
    ]

    await update.message.reply_text(
        f"👋 Welcome *{user.username}*\n\n"
        "Daily max 5 tasks allowed.\n"
        "After tasks, earn via referrals.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- TASK MENU ----------------
async def task_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    done = users[uid]["tasks_done"]

    if done >= MAX_TASKS:
        await query.edit_message_text(
            "✅ You are done for today.\n\n"
            "Invite users and earn *10%* of their income.\n"
            "New tasks will come *tomorrow*.",
            parse_mode="Markdown"
        )
        return

    buttons = []
    for i in range(1, MAX_TASKS + 1):
        buttons.append([InlineKeyboardButton(f"Task {i}", callback_data=f"task_{i}")])

    await query.edit_message_text(
        "🧑‍💻 *Select a task:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ---------------- OPEN TASK ----------------
async def open_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    task_no = int(query.data.split("_")[1])

    if task_no != users[uid]["tasks_done"] + 1:
        await query.edit_message_text("❌ Complete tasks in order.")
        return

    text = TASK_TEXTS[task_no] + "\n\n"
    text += "❗ Admin has activity data.\n"
    text += "Cheating will be caught."

    keyboard = [
        [
            InlineKeyboardButton("✅ Yes, Completed", callback_data="task_yes"),
            InlineKeyboardButton("❌ No", callback_data="task_no")
        ]
    ]

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )

# ---------------- TASK CONFIRM ----------------
async def task_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    if query.data == "task_yes":
        users[uid]["tasks_done"] += 1
        users[uid]["balance"] += 20  # fixed, not shown to user

        await query.edit_message_text(
            "✅ Task recorded.\n\n"
            "To unlock next task:\n"
            "👉 Invite *1 new user*.\n\n"
            "Your referral link is in *Refer & Earn*.",
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text("Complete the task first, then confirm.")

# ---------------- REFER ----------------
async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    bot_username = context.bot.username
    link = f"https://t.me/{bot_username}?start={uid}"

    await query.edit_message_text(
        "👥 *Refer & Earn*\n\n"
        "Earn *10%* of your referral’s income.\n\n"
        f"🔗 Your link:\n{link}",
        parse_mode="Markdown"
    )

# ---------------- WITHDRAW ----------------
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id
    bal = users[uid]["balance"]

    if bal < MIN_WITHDRAW:
        await query.edit_message_text(
            f"❌ Minimum withdraw is *{MIN_WITHDRAW}*.\n"
            f"Your balance: *{bal}*",
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text(
            "✅ Withdraw request received.\n"
            "Admin will process it soon.",
            parse_mode="Markdown"
        )

# ---------------- WARNING ----------------
async def warning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "⚠️ *Warning*\n\n"
        "Multiple accounts, fake referrals,\n"
        "or cheating will lead to ban.",
        parse_mode="Markdown"
    )

# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(task_menu, pattern="tasks"))
    app.add_handler(CallbackQueryHandler(open_task, pattern="task_\\d"))
    app.add_handler(CallbackQueryHandler(task_confirm, pattern="task_yes|task_no"))
    app.add_handler(CallbackQueryHandler(refer, pattern="refer"))
    app.add_handler(CallbackQueryHandler(withdraw, pattern="withdraw"))
    app.add_handler(CallbackQueryHandler(warning, pattern="warning"))

    app.run_polling()

if __name__ == "__main__":
    main()
