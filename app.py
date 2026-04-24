from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

BOT_TOKEN = "8290672651:AAEdi86fVQXo8XpTOYWxARvhQHdUETjWjAg"

users = set()
last_command = "S"
capture_flag = False
esp32_online = False
last_update_id = 0

# ================= TELEGRAM =================
def update_users():
    global capture_flag, last_update_id

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update_id+1}"
    res = requests.get(url).json()

    if "result" in res:
        for msg in res["result"]:
            last_update_id = msg["update_id"]

            try:
                chat_id = msg["message"]["chat"]["id"]
                users.add(chat_id)

                text = msg["message"].get("text", "")

                if text in ["hi", "/start"]:
                    send_telegram("🚗 Commands:\n/capture\n/status")

                elif text == "/capture":
                    capture_flag = True
                    print("📸 Capture flag TRUE")
                    send_telegram("📸 Capture requested")

                elif text == "/status":
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
            files={"photo": ("image.jpg", img)}
        )

# ================= WEB =================
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

# ================= ESP32 =================
@app.route('/get_command')
def get_command():
    global capture_flag, esp32_online

    esp32_online = True

    # 🔥 IMPORTANT: process telegram HERE
    update_users()

    if capture_flag:
        capture_flag = False
        print("🚀 Sending CAPTURE")
        return "CAPTURE"

    return last_command

# ================= IMAGE =================
@app.route('/predict', methods=['POST'])
def predict():
    img_bytes = request.data

    send_telegram("🌿 Disease: Leaf Spot")
    send_image(img_bytes)

    return jsonify({"ok": True})

# ================= RUN =================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)