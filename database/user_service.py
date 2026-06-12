from datetime import datetime

from database.firebase_config import db


def save_user(user):
    """
    Store Telegram user information in Firestore.
    """

    user_data = {
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "joined_at": datetime.now(),
    }

    db.collection("users").document(str(user.id)).set(user_data)

    print(f"User record stored: {user.first_name}")
