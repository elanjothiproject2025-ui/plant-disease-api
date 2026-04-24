from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
import requests
import os

app = Flask(__name__)

BOT_TOKEN = "8290672651:AAEdi86fVQXo8XpTOYWxARvhQHdUETjWjAg"

users = set()
last_command = "S"
capture_flag = False
esp32_online = False

def update_users():
    global capture_flag

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    res = requests.get(url).json()

    if "result" in res:
        for msg in res["result"]:
            try:
                chat_id = msg["message"]["chat"]["id"]
                users.add(chat_id)

                text = msg["message"].get("text", "")

                if text in ["hi", "/start"]:
                    send_telegram(
                        "🚗 Commands:\n"
                        "/capture → take image\n"
                        "/status → check ESP32\n"
                        "Web → control rover"
                    )

                if text == "/capture":
                    capture_flag = True
                    send_telegram("📸 Capture requested")

                if text == "/status":
                    send_telegram("✅ ESP32 ONLINE" if esp32_online else "❌ ESP32 OFFLINE")

            except:
                pass

def send_telegram(msg):
    for chat_id in users:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": chat_id, "text": msg}
        )

def send_image(img):
    for chat_id in users:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
            data={"chat_id": chat_id},
            files={"photo": ("img.jpg", img)}
        )

@app.route('/')
def home():
    return '''
    <h2>🚗 Rover Control</h2>
    <button onclick="send('F')">Forward</button><br><br>
    <button onclick="send('L')">Left</button>
    <button onclick="send('S')">Stop</button>
    <button onclick="send('R')">Right</button><br><br>
    <button onclick="send('B')">Backward</button>

    <br><br>
    <input type="range" min="0" max="180" onchange="servo(this.value)">
    
    <script>
    function send(cmd){ fetch('/control?cmd='+cmd); }
    function servo(v){ fetch('/control?cmd=SERVO:'+v); }
    </script>
    '''

@app.route('/control')
def control():
    global last_command
    last_command = request.args.get("cmd", "S")
    return "OK"

@app.route('/get_command')
def get_command():
    global capture_flag, esp32_online
    esp32_online = True
    update_users()

    if capture_flag:
        capture_flag = False
        return "CAPTURE"

    return last_command

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['image']
    img_bytes = file.read()

    result = "Leaf Spot"
    confidence = 0.92

    send_telegram(f"🌿 {result} ({confidence})")
    send_image(img_bytes)

    return jsonify({"result": result})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)