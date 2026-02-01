from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "8241094570:AAE-o2lCKaKlCnxTdOA7XEtw29P9i_EOi-4"

# ===== USER DATA =====
users = {}

# ===== TASKS =====
TASKS = {
    1: "Task 1:\nVisit & complete:\nhttps://web.earnbox.net/h5/#/?salt=E2psxuKVMn",
    2: "Task 2:\nVisit & complete:\nhttps://www.effectivegatecpm.com/u39c97tf?key=311b89465707b46bd5a609ac8ff9466c",
    3: "Task 3:\nVisit & complete:\nhttps://web.cashin.life/?salt=ltZV7TKeyz",
    4: "Task 4:\nDownload app & send ₹1 to anyone:\nhttps://r.navi.com/7NFTJB",
    5: "Task 5:\nVisit & complete:\nhttps://www.effectivegatecpm.com/u39c97tf?key=311b89465707b46bd5a609ac8ff9466c",
}

# ===== START COMMAND =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args

    # NEW USER INIT
    if user_id not in users:
        users[user_id] = {"task": 1, "ref": 0}

        # REFERRAL PROCESS
        if args:
            ref_id = int(args[0])
            if ref_id in users and ref_id != user_id:
                users[ref_id]["ref"] += 1

    await send_task(update, context)

# ===== SEND TASK FUNCTION =====
async def send_task(update, context):
    user_id = update.effective_user.id
    user = users[user_id]
    task_no = user["task"]

    if task_no > 5:
        await update.message.reply_text("✅ All tasks completed.\nWait for admin verification.")
        return

    # REFERRAL LOCK CHECK
    if user["ref"] < task_no - 1:
        link = f"https://t.me/{context.bot.username}?start={user_id}"
        await update.message.reply_text(
            f"❌ Next task locked.\n\n"
            f"👉 Refer 1 more friend to unlock Task {task_no}\n\n"
            f"Your referral link:\n{link}"
        )
        return

    # SHOW TASK WITH YES/NO BUTTONS
    keyboard = [
        [InlineKeyboardButton("✅ Task Completed", callback_data=f"done_{task_no}")],
        [InlineKeyboardButton("❌ Not Done Yet", callback_data="notdone")]
    ]

    await update.message.reply_text(
        TASKS[task_no] + "\n\n⚠️ Admin is tracking all activity.\nCheating will be caught.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== BUTTON HANDLER =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if data == "notdone":
        await query.message.reply_text("❌ Complete the task first, then tap DONE.")
        return

    if data.startswith("done_"):
        task_no = int(data.split("_")[1])

        if users[user_id]["task"] == task_no:
            users[user_id]["task"] += 1
            await query.message.reply_text(
                "✅ Task submitted.\nRefer 1 friend to unlock next task."
            )
            await send_task(query, context)

# ===== RUN BOT =====
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.run_polling()
