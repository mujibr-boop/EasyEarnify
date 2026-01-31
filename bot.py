import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ---------------- BOT TOKEN ----------------
BOT_TOKEN = "8241094570:AAE-o2lCKaKlCnxTdOA7XEtw29P9i_EOi-4"

# ---------------- LOGGING ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ---------------- DATA ----------------
FORCE_JOIN_CHANNELS = [
    "https://t.me/incomelooops",
    "https://t.me/reviewworklive",
    "https://t.me/earnbyrealbotnow"
]

TASK_LINKS = [
    "https://web.earnbox.net/h5/#/?salt=E2psxuKVMn",  # Task 1
    "https://www.effectivegatecpm.com/u39c97tf?key=311b89465707b46bd5a609ac8ff9466c",  # Task 2
    "https://web.cashin.life/?salt=ltZV7TKeyz",  # Task 3
    "https://r.navi.com/7NFTJB",  # Task 4 (wallet activation, send 1₹)
    "https://www.effectivegatecpm.com/u39c97tf?key=311b89465707b46bd5a609ac8ff9466c"  # Task 5
]

USER_DATA = {}  # {user_id: {"points": 0.0, "task": 0, "referrals": 0}}

# ---------------- HELPERS ----------------
def check_user_data(user_id):
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {"points": 0.0, "task": 0, "referrals": 0}

def get_keyboard(user_id):
    check_user_data(user_id)
    task_num = USER_DATA[user_id]["task"]
    keyboard = []
    if task_num < 5:
        keyboard.append([InlineKeyboardButton(f"Task {task_num + 1}", callback_data=f"task_{task_num + 1}")])
    keyboard.append([InlineKeyboardButton("Withdraw", callback_data="withdraw")])
    keyboard.append([InlineKeyboardButton("Refer & Earn", callback_data="refer")])
    keyboard.append([InlineKeyboardButton("Warning", callback_data="warning")])
    return InlineKeyboardMarkup(keyboard)

# ---------------- COMMANDS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    check_user_data(user.id)

    msg = f"Hello {user.first_name} 👋\n\nWelcome to EasyEarnify 💎\n\n" \
          "Please join all 3 channels to start earning:\n"
    for ch in FORCE_JOIN_CHANNELS:
        msg += f"{ch}\n"

    await update.message.reply_text(msg, reply_markup=get_keyboard(user.id))

# ---------------- CALLBACKS ----------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    check_user_data(user.id)
    data = query.data
    task_num = USER_DATA[user.id]["task"]

    # ---------------- TASK BUTTONS ----------------
    if data.startswith("task_"):
        selected_task = int(data.split("_")[1])
        if selected_task != task_num + 1:
            await query.answer("Complete previous task first!", show_alert=True)
            return

        # Give points 8-10 with decimal
        points = round(random.uniform(8, 10), 2)
        USER_DATA[user.id]["points"] += points
        USER_DATA[user.id]["task"] += 1

        # Task messages
        if selected_task <= 5:
            link = TASK_LINKS[selected_task - 1]
            extra_msg = ""
            if selected_task == 4:
                extra_msg = "\nActivate your wallet by sending 1₹ to anyone inside the app."
            await query.edit_message_text(
                f"Task {selected_task}: Complete the task at the link below:\n{link}{extra_msg}\n"
                f"Points earned: {points}\n\nClick 'Task {selected_task}' again after completion.",
                reply_markup=get_keyboard(user.id)
            )
        if selected_task == 5:
            await query.answer(f"Task 5 done ✅ Total points: {USER_DATA[user.id]['points']}", show_alert=True)
            await query.edit_message_text(
                f"You completed 5 tasks today!\nTotal points: {USER_DATA[user.id]['points']}\n\n"
                "New tasks will be available tomorrow. Invite friends to earn 10% of their points in the meantime.",
                reply_markup=get_keyboard(user.id)
            )
        else:
            await query.answer(f"You earned {points} points! 🎉", show_alert=True)

    # ---------------- REFERRAL ----------------
    elif data == "refer":
        await query.answer(
            "Share your bot link with friends. Earn 10% of points from valid referrals!", show_alert=True
        )

    # ---------------- WITHDRAW ----------------
    elif data == "withdraw":
        await query.answer(f"You have {USER_DATA[user.id]['points']} points available.", show_alert=True)

    # ---------------- WARNING ----------------
    elif data == "warning":
        await query.answer("Do not click random links outside the bot! ⚠️", show_alert=True)

# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
