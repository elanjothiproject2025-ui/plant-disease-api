from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
import requests
import os

app = Flask(__name__)

# ================== TELEGRAM CONFIG ==================
BOT_TOKEN = "8290672651:AAEdi86fVQXo8XpTOYWxARvhQHdUETjWjAg"

# Store all users (multi-user support)
users = set()

def update_users():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        res = requests.get(url).json()

        if "result" in res:
            for msg in res["result"]:
                try:
                    chat_id = msg["message"]["chat"]["id"]
                    users.add(chat_id)
                except:
                    pass
    except:
        print("Error fetching users")

def send_telegram(msg):
    update_users()

    for chat_id in users:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(url, data={
                "chat_id": chat_id,
                "text": msg
            })
        except:
            print(f"Failed to send message to {chat_id}")

# ================== API ROUTE ==================
@app.route('/predict', methods=['POST'])
def predict():
    try:
        file = request.files['image']

        # Basic image processing
        img = Image.open(file).resize((224, 224))
        img = np.array(img) / 255.0

        # Dummy fast detection (cloud friendly)
        result = "Leaf Spot"
        confidence = 0.92

        # Send Telegram alert
        msg = f"Disease: {result}\nConfidence: {confidence:.2f}"
        send_telegram(msg)

        return jsonify({
            "disease": result,
            "confidence": confidence
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# ================== HOME ==================
@app.route('/')
def home():
    return "Plant Disease API Running (Online)"

# ================== RUN ==================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)