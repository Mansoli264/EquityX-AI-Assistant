import json
import os

import firebase_admin
from firebase_admin import credentials, firestore

firebase_json = os.getenv("FIREBASE_CREDENTIALS")

if not firebase_json:
    raise ValueError("FIREBASE_CREDENTIALS not found")

# Convert escaped characters into real JSON
firebase_json = firebase_json.encode().decode("unicode_escape")

firebase_dict = json.loads(firebase_json)

if not firebase_admin._apps:
    firebase_admin.initialize_app(credentials.Certificate(firebase_dict))

db = firestore.client()

print("Firebase connection established.")
