from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ====== BOT TOKEN ======
BOT_TOKEN = "8241094570:AAE-o2lCKaKlCnxTdOA7XEtw29P9i_EOi-4"

# ====== IN-MEMORY STORAGE ======
user_progress = {}

# ====== START ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_progress[user_id] = 1

    await update.message.reply_text(
        "Welcome 👋\n\n"
        "Complete tasks step by step.\n"
        "⚠️ Admin has full data tracking.\n"
        "Cheating = permanent ban."
    )
    await show_tasks(update, context)

# ====== TASK MENU ======
async def show_tasks(update, context):
    keyboard = [
        [InlineKeyboardButton("Task 1", callback_data="task_1")],
        [InlineKeyboardButton("Task 2", callback_data="task_2")],
        [InlineKeyboardButton("Task 3", callback_data="task_3")],
        [InlineKeyboardButton("Task 4", callback_data="task_4")],
        [InlineKeyboardButton("Task 5", callback_data="task_5")]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Select your task 👇", reply_markup=markup)
    else:
        await update.callback_query.message.reply_text("Select your task 👇", reply_markup=markup)

# ====== TASK CLICK ======
async def task_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    task_no = int(query.data.split("_")[1])
    user_id = query.from_user.id

    if user_progress.get(user_id, 1) != task_no:
        await query.message.reply_text(
            "❌ Complete previous task first."
        )
        return

    # 🔗 Hidden link inside text (example)
    task_text = (
        f"📌 *Task {task_no}*\n\n"
        "Complete the task mentioned here.\n"
        "🔗 Click the text below:\n"
        "[Complete Task](https://example.com)\n\n"
        "⚠️ Admin can verify everything."
    )

    await query.message.reply_text(
        task_text,
        parse_mode="Markdown"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Yes, Completed", callback_data=f"done_{task_no}")],
        [InlineKeyboardButton("❌ No", callback_data="not_done")]
    ]
    await query.message.reply_text(
        "Have you completed the task?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ====== TASK DONE ======
async def task_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    task_no = int(query.data.split("_")[1])
    user_id = query.from_user.id

    if user_progress.get(user_id, 1) != task_no:
        await query.message.reply_text("Invalid action.")
        return

    user_progress[user_id] += 1

    await query.message.reply_text(
        "✅ Task recorded.\n\n"
        "👉 Refer *1 new member* to unlock next task.\n"
        "Admin is monitoring referrals.",
        parse_mode="Markdown"
    )

# ====== NOT DONE ======
async def not_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "❌ Complete the task honestly.\nAdmin has data."
    )

# ====== APP START ======
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(task_click, pattern="^task_"))
app.add_handler(CallbackQueryHandler(task_done, pattern="^done_"))
app.add_handler(CallbackQueryHandler(not_done, pattern="^not_done$"))

app.run_polling()
