from datetime import datetime

from database.firebase_config import db


def save_feedback(user, feedback):

    # Save user feedback.

    feedback_data = {
        "user_id": user.id,
        "username": user.username,
        "feedback": feedback,
        "created_at": datetime.now(),
    }

    db.collection("feedbacks").add(feedback_data)

    print(f"Feedback received from {user.first_name}")
