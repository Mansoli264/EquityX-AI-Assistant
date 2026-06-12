from datetime import datetime

from database.firebase_config import db


def save_chat(user, user_message, bot_response):

    # Store user conversations in Firestore.

    chat_data = {
        "user_id": user.id,
        "username": user.username,
        "message": user_message,
        "response": bot_response,
        "timestamp": datetime.now(),
    }

    db.collection("chat_history").add(chat_data)

    print(f"Chat record stored successfully for {user.first_name}")


def get_chat_stats():

    # Return total chat count per user.

    stats = {}

    chats = db.collection("chat_history").stream()

    for chat in chats:

        data = chat.to_dict()

        username = data.get("username", "Unknown")

        stats[username] = stats.get(username, 0) + 1

    return stats
