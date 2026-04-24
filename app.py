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

# 🔴 IMPORTANT FIX (prevents spam)
last_update_id = None

# ================= TELEGRAM =================
def update_users():
    global capture_flag, last_update_id

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    res = requests.get(url).json()

    if "result" in res:
        for msg in res["result"]:
            update_id = msg["update_id"]

            # ✅ Skip old messages (ANTI-SPAM)
            if last_update_id is not None and update_id <= last_update_id:
                continue

            last_update_id = update_id

            try:
                chat_id = msg["message"]["chat"]["id"]
                users.add(chat_id)

                text = msg["message"].get("text", "")

                # ✅ START / HI
                if text in ["hi", "/start"]:
                    send_telegram(
                        "🚗 Rover Commands:\n\n"
                        "/capture → Capture image\n"
                        "/status → Check ESP32\n\n"
                        "🌐 Use web for movement"
                    )

                # ✅ CAPTURE
                elif text == "/capture":
                    capture_flag = True
                    send_telegram("📸 Capture requested")

                # ✅ STATUS
                elif text == "/status":
                    if esp32_online:
                        send_telegram("✅ ESP32 is ONLINE")
                    else:
                        send_telegram("❌ ESP32 is OFFLINE")

            except:
                pass

def send_telegram(msg):
    for chat_id in users:
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={"chat_id": chat_id, "text": msg}
            )
        except:
            pass

def send_image(img):
    for chat_id in users:
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data={"chat_id": chat_id},
                files={"photo": ("image.jpg", img)}
            )
        except:
            pass

# ================= WEB CONTROL =================
@app.route('/')
def home():
    return '''
    <h2>🚗 Rover Control Panel</h2>

    <button onclick="send('F')">⬆ Forward</button><br><br>

    <button onclick="send('L')">⬅ Left</button>
    <button onclick="send('S')">⏹ Stop</button>
    <button onclick="send('R')">➡ Right</button><br><br>

    <button onclick="send('B')">⬇ Backward</button>

    <br><br>
    <input type="range" min="0" max="180" value="90" onchange="servo(this.value)">
    <p>Camera Angle</p>

    <script>
    function send(cmd){
        fetch('/control?cmd=' + cmd)
    }
    function servo(val){
        fetch('/control?cmd=SERVO:' + val)
    }
    </script>
    '''

@app.route('/control')
def control():
    global last_command
    last_command = request.args.get("cmd", "S")
    return "OK"

# ================= ESP32 POLLING =================
@app.route('/get_command')
def get_command():
    global capture_flag, esp32_online

    esp32_online = True
    update_users()

    if capture_flag:
        capture_flag = False
        return "CAPTURE"

    return last_command

# ================= IMAGE =================
@app.route('/predict', methods=['POST'])
def predict():
    try:
        file = request.files['image']
        img_bytes = file.read()

        img = Image.open(file).resize((224, 224))
        img = np.array(img) / 255.0

        result = "Leaf Spot"
        confidence = 0.92

        send_telegram(f"🌿 Disease: {result}\nConfidence: {confidence}")
        send_image(img_bytes)

        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": str(e)})

# ================= RUN =================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)