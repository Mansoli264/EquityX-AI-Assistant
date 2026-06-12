from datetime import datetime

from database.firebase_config import db


def create_support_ticket(user, issue):

    # Create a support request.

    ticket_data = {
        "user_id": user.id,
        "username": user.username,
        "issue": issue,
        "status": "Open",
        "created_at": datetime.now(),
    }

    db.collection("support_tickets").add(ticket_data)

    print(f"Support request created for {user.first_name}")
