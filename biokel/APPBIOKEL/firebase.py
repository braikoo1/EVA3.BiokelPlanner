import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings
import os

def init_firebase():
    if not firebase_admin._apps:
        cred_path = os.path.join(settings.BASE_DIR, "biokelaccountservice.json")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

def get_db():
    init_firebase()
    return firestore.client()