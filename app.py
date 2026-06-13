# IMPORTS

import asyncio
import os
import threading

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# LOAD ENV VARIABLES


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError(" BOT_TOKEN not found in .env file")


# FIREBASE DATABASE


from chatbot.ai_handler import get_ai_response
from database.chat_service import save_chat
from database.feedback_service import save_feedback
from database.firebase_config import db
from database.support_service import create_support_ticket
from database.user_service import save_user

# SERVICES


# FLASK APP


app = Flask(__name__)


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect("/login")


app.secret_key = os.getenv("SECRET_KEY", "development-secret-key")


@app.route("/admin")
@login_required
def admin_home():
    return redirect("/admin/dashboard")


# LOGIN MANAGER


login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"


# ADMIN CLASS


class Admin(UserMixin):

    def __init__(self, id):
        self.id = id


# LOAD USER


@login_manager.user_loader
def load_user(user_id):
    return Admin(user_id)


# LOGIN PAGE


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        admin_username = os.getenv("ADMIN_USERNAME")
        admin_password = os.getenv("ADMIN_PASSWORD")

        if not admin_username or not admin_password:
            raise ValueError("Admin credentials missing in environment variables.")

        if username == admin_username and password == admin_password:

            user = Admin(id=1)

            login_user(user)

            return redirect("/admin")

    return render_template("admin/login.html")


# TELEGRAM APPLICATION


telegram_app = Application.builder().token(BOT_TOKEN).build()


# START COMMAND


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    save_user(update.effective_user)

    welcome_message = """
 Welcome to EquityX AI Assistant

Available Features:

• Market Education
• Trading Concepts
• Technical Analysis
• Investment Fundamentals

Available Commands:
/about
/services
/courses
/kyc
/contact
/register
/support
/feedback

Ask me anything related to:
 Stock Market
 Trading
 Investing
 Technical Analysis
"""

    await update.message.reply_text(welcome_message)


# ABOUT COMMAND


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = """
About EquityX

EquityX is an AI-powered stock market education platform.

Our mission:
• Simplify trading education
• Help traders grow professionally
• Provide AI-powered support
"""

    await update.message.reply_text(message)


# SERVICES COMMAND


async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = """
 Our Services

• Trading Education
• Technical Analysis
• AI Trading Support
• Risk Management Guidance
"""

    await update.message.reply_text(message)


# COURSES COMMAND


async def courses(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = """
 Available Courses

1. Beginner Trading
2. Technical Analysis
3. Advanced Trading
4. Risk Management
"""

    await update.message.reply_text(message)


# KYC COMMAND


async def kyc(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = """
 KYC Process

Required Documents:
• PAN Card
• Aadhaar Card
• Passport Photo
• Bank Details
"""

    await update.message.reply_text(message)


# CONTACT COMMAND


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = """
 Contact Us

Email: support@equityx.ai
Phone: Available upon request
"""

    await update.message.reply_text(message)


# REGISTER COMMAND


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = """
 Registration Process

1. Share Full Name
2. Share Email
3. Share Experience Level
"""

    await update.message.reply_text(message)


# SUPPORT COMMAND


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):

    issue = " ".join(context.args)

    if not issue:

        await update.message.reply_text(
            "Example:\n/support My account login is not working"
        )

        return

    create_support_ticket(update.effective_user, issue)

    await update.message.reply_text("Support ticket created successfully.")


# FEEDBACK COMMAND


async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    feedback_text = " ".join(context.args)

    if not feedback_text:

        await update.message.reply_text("Example:\n/feedback Excellent AI support")

        return

    save_feedback(update.effective_user, feedback_text)

    await update.message.reply_text("Thank you for your feedback.")


# AI CHAT FUNCTION


async def keep_typing(update, context):

    while True:

        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )

        await asyncio.sleep(4)


async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_message = update.message.text

    typing_task = asyncio.create_task(keep_typing(update, context))

    try:

        ai_response = await asyncio.wait_for(
            asyncio.to_thread(get_ai_response, user_message), timeout=10
        )

        save_chat(update.effective_user, user_message, ai_response)

        MAX_LENGTH = 4000

        for i in range(0, len(ai_response), MAX_LENGTH):

            await update.message.reply_text(ai_response[i : i + MAX_LENGTH])

    except asyncio.TimeoutError:

        await update.message.reply_text(
            "The assistant is taking too long to respond. Please try again in a moment."
        )

    except Exception as e:

        print(f"Message Handler Error: {str(e)}")

        await update.message.reply_text(
            "The assistant is currently unavailable. Please try again later."
        )

    finally:

        typing_task.cancel()


# HOME ROUTE


@app.route("/")
def home():

    return {"application": "EquityX AI Assistant", "status": "running"}


# ADMIN DASHBOARD


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    users = db.collection("users").get()
    chats = db.collection("chat_history").get()
    feedbacks = db.collection("feedbacks").get()
    tickets = db.collection("support_tickets").get()

    return render_template(
        "admin/dashboard.html",
        total_users=len(users),
        total_chats=len(chats),
        total_feedbacks=len(feedbacks),
        total_tickets=len(tickets),
    )


# ADMIN USERS


@app.route("/admin/users")
@login_required
def admin_users():

    users_ref = db.collection("users").stream()

    users = [user.to_dict() for user in users_ref]

    return render_template("admin/users.html", users=users)


# ADMIN CHAT PAGE


@app.route("/admin/chats")
@login_required
def admin_chats():

    search = request.args.get("search", "").lower().strip()

    chats_ref = db.collection("chat_history").stream()

    chats = []

    for chat in chats_ref:

        # Convert Firebase document to dictionary
        chat_data = chat.to_dict()

        # Add Firebase document ID
        chat_data["id"] = chat.id

        # Safe values
        username = str(chat_data.get("username", "")).lower()
        message = str(chat_data.get("message", "")).lower()
        response = str(chat_data.get("response", "")).lower()

        # Search Filter
        if (
            search == ""
            or search in username
            or search in message
            or search in response
        ):
            chats.append(chat_data)

    print(f"Search results returned: {len(chats)}")

    return render_template("admin/chats.html", chats=chats, search=search)


# DELETE CHAT


@app.route("/delete-chat/<chat_id>")
@login_required
def delete_chat(chat_id):

    db.collection("chat_history").document(chat_id).delete()

    return redirect("/admin/chats")


# ADMIN FEEDBACKS


@app.route("/admin/feedbacks")
@login_required
def admin_feedbacks():

    feedback_ref = db.collection("feedbacks").stream()

    feedbacks = [feedback.to_dict() for feedback in feedback_ref]

    return render_template("admin/feedbacks.html", feedbacks=feedbacks)


# ADMIN SUPPORT


@app.route("/admin/support")
@login_required
def admin_support():

    tickets_ref = db.collection("support_tickets").stream()

    tickets = [ticket.to_dict() for ticket in tickets_ref]

    return render_template("admin/support.html", tickets=tickets)


from database.chat_service import get_chat_stats


@app.route("/admin/analytics")
@login_required
def analytics():

    stats = get_chat_stats()

    labels = list(stats.keys())
    values = list(stats.values())

    return render_template("admin/analytics.html", labels=labels, values=values)


# TELEGRAM HANDLERS

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("about", about))
telegram_app.add_handler(CommandHandler("services", services))
telegram_app.add_handler(CommandHandler("courses", courses))
telegram_app.add_handler(CommandHandler("kyc", kyc))
telegram_app.add_handler(CommandHandler("contact", contact))
telegram_app.add_handler(CommandHandler("register", register))
telegram_app.add_handler(CommandHandler("support", support))
telegram_app.add_handler(CommandHandler("feedback", feedback))

telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_message))


# RUN FLASK


def run_flask():

    port = int(os.environ.get("PORT", 5050))

    app.run(host="0.0.0.0", port=port, debug=False)


# MAIN


if __name__ == "__main__":

    mode = os.getenv("APP_MODE", "local")

    print(f"Starting in {mode} mode")

    flask_thread = threading.Thread(target=run_flask)

    flask_thread.start()

    telegram_app.run_polling(poll_interval=3, timeout=30, drop_pending_updates=True)
