# firebase_config.py

import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase
cred = credentials.Certificate("firebase_key.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://baby-detection-c40a9-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

def send_event(event):
    try:
        ref = db.reference("events")
        ref.push(event)
    except Exception as e:
        print("Firebase Error:", e)

# 🔥 NEW FUNCTION (for remote control)
def get_control_status():
    try:
        ref = db.reference("control/status")
        status = ref.get()
        return status if status else "off"
    except Exception as e:
        print("Control Error:", e)
        return "off"
    
def get_safe_zone():
    try:
        ref = db.reference("safe_zone")
        return ref.get()
    except:
        return None