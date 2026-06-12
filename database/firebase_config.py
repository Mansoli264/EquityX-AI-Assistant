import json
import os

import firebase_admin
from firebase_admin import credentials, firestore

firebase_file = "KT TG AI bot.json"

if os.path.exists(firebase_file):

    cred = credentials.Certificate(firebase_file)

else:

    firebase_json = os.getenv("FIREBASE_CREDENTIALS")

    if not firebase_json:

        raise ValueError("Firebase credentials not found.")

    firebase_dict = json.loads(firebase_json)

    cred = credentials.Certificate(firebase_dict)

if not firebase_admin._apps:

    firebase_admin.initialize_app(cred)

db = firestore.client()

print("Firebase connection established.")
