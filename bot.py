from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import sqlite3

TOKEN = "8241094570:AAE-o2lCKaKlCnxTdOA7XEtw29P9i_EOi-4"

# ================= DATABASE =================
conn = sqlite3.connect("data.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    ref_by INTEGER,
    referrals INTEGER DEFAULT 0,
    task INTEGER DEFAULT 1
)
""")
conn.commit()

# ================= HELPERS =================
def get_user(user_id):
    cur.execute("SELECT referrals, task FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if not row:
        cur.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        return 0, 1
    return row

def add_referral(referrer_id):
    cur.execute("UPDATE users SET referrals = referrals + 1 WHERE user_id=?", (referrer_id,))
    conn.commit()

def next_task(user_id):
    cur.execute("UPDATE users SET task = task + 1 WHERE user_id=?", (user_id,))
    conn.commit()

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if context.args:
        referrer = int(context.args[0])
        if referrer != user_id:
            cur.execute("SELECT ref_by FROM users WHERE user_id=?", (user_id,))
            chk = cur.fetchone()
            if not chk or chk[0] is None:
                cur.execute("UPDATE users SET ref_by=? WHERE user_id=?", (referrer, user_id))
                add_referral(referrer)
                conn.commit()

    get_user(user_id)

    kb = [[InlineKeyboardButton("📝 Start Task", callback_data="task")]]
    await update.message.reply_text(
        "Welcome.\n\nTasks unlock step-by-step.\nReferral required after every task.\n\n⚠️ Admin tracks everything.",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= TASK =================
TASKS = {
    1: "TASK 1\n\nComplete this task.\nHidden link inside this text 👉 https://example.com/1",
    2: "TASK 2\n\nFollow instructions carefully 👉 https://example.com/2",
    3: "TASK 3\n\nDo not skip steps 👉 https://example.com/3",
    4: "TASK 4\n\nStrict checking 👉 https://example.com/4",
    5: "TASK 5\n\nFinal task 👉 https://example.com/5"
}

async def task_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id

    refs, task = get_user(user_id)

    if task > 5:
        await q.edit_message_text("✅ All tasks completed.")
        return

    if refs < task - 1:
        link = f"https://t.me/{context.bot.username}?start={user_id}"
        await q.edit_message_text(
            f"❌ Task locked.\n\nRefer 1 user to continue.\n\nYour link:\n{link}\n\n⚠️ Cheating = Ban"
        )
        return

    kb = [
        [InlineKeyboardButton("✅ YES, completed", callback_data="done")],
        [InlineKeyboardButton("❌ NO", callback_data="no")]
    ]

    await q.edit_message_text(TASKS[task], reply_markup=InlineKeyboardMarkup(kb))

# ================= CONFIRM =================
async def done_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id

    refs, task = get_user(user_id)

    if refs < task:
        link = f"https://t.me/{context.bot.username}?start={user_id}"
        await q.edit_message_text(
            f"⚠️ Completion detected.\n\nReferral missing.\n\nRefer 1 user:\n{link}\n\nAdmin has full data."
        )
        return

    next_task(user_id)

    if task == 5:
        await q.edit_message_text("✅ All tasks finished.\nWait for further instructions.")
        return

    kb = [[InlineKeyboardButton("📝 Next Task", callback_data="task")]]
    await q.edit_message_text(
        f"✅ Task {task} verified.\n\nRefer 1 more user to unlock next task.",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ================= NO =================
async def no_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Complete the task properly, then confirm.")

# ================= RUN =================
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(task_handler, pattern="task"))
app.add_handler(CallbackQueryHandler(done_handler, pattern="done"))
app.add_handler(CallbackQueryHandler(no_handler, pattern="no"))

app.run_polling()
