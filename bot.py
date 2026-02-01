from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"

user_task = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_task[update.effective_user.id] = 0
    await update.message.reply_text(
        "Welcome 👋\n\nComplete tasks step by step.\nCheating will be caught by admin."
    )
    await show_tasks(update, context)

async def show_tasks(update, context):
    keyboard = [
        [InlineKeyboardButton("Task 1", callback_data="task_1")],
        [InlineKeyboardButton("Task 2", callback_data="task_2")],
        [InlineKeyboardButton("Task 3", callback_data="task_3")],
        [InlineKeyboardButton("Task 4", callback_data="task_4")],
        [InlineKeyboardButton("Task 5", callback_data="task_5")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Choose a task 👇", reply_markup=reply_markup)
    else:
        await update.callback_query.message.reply_text("Choose a task 👇", reply_markup=reply_markup)

async def task_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    task_no = query.data.split("_")[1]
    await query.message.reply_text(
        f"Task {task_no} details hidden in text.\n\n"
        "Complete the task.\n\n"
        "Admin has tracking data.\n"
        "If you cheat, you will be caught."
    )

    keyboard = [
        [InlineKeyboardButton("✅ Yes, Completed", callback_data=f"done_{task_no}")],
        [InlineKeyboardButton("❌ No", callback_data="not_done")]
    ]
    await query.message.reply_text(
        "Have you completed the task?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def task_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "Task recorded ✅\n\n"
        "Refer **1 more member** to proceed to the next task."
    )

async def not_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Complete the task first to continue.")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(task_click, pattern="task_"))
app.add_handler(CallbackQueryHandler(task_done, pattern="done_"))
app.add_handler(CallbackQueryHandler(not_done, pattern="not_done"))

app.run_polling()
