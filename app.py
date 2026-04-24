from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
import requests
import os

app = Flask(__name__)

# ================== TELEGRAM CONFIG ==================
BOT_TOKEN = "8290672651:AAEdi86fVQXo8XpTOYWxARvhQHdUETjWjAg"

users = set()
last_command = "S"
capture_flag = False

# ================== TELEGRAM ==================
def update_users():
    global capture_flag

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        res = requests.get(url).json()

        if "result" in res:
            for msg in res["result"]:
                try:
                    chat_id = msg["message"]["chat"]["id"]
                    users.add(chat_id)

                    text = msg["message"].get("text", "")

                    if text == "/capture":
                        capture_flag = True

                except:
                    pass
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

# ================== WEB CONTROL ==================
@app.route('/')
def home():
    return '''
    <h2>🚗 Rover Control Panel</h2>

    <button onclick="send('F')">⬆ Forward</button><br><br>

    <button onclick="send('L')">⬅ Left</button>
    <button onclick="send('S')">⏹ Stop</button>
    <button onclick="send('R')">➡ Right</button><br><br>

    <button onclick="send('B')">⬇ Backward</button>

    <script>
    function send(cmd){
        fetch('/control?cmd=' + cmd)
    }
    </script>
    '''

@app.route('/control')
def control():
    global last_command
    last_command = request.args.get("cmd", "S")
    return "OK"

# ================== ESP32 POLLING ==================
@app.route('/get_command')
def get_command():
    global capture_flag

    update_users()

    if capture_flag:
        capture_flag = False
        return "CAPTURE"

    return last_command

# ================== IMAGE UPLOAD ==================
@app.route('/predict', methods=['POST'])
def predict():
    try:
        file = request.files['image']

        img = Image.open(file).resize((224, 224))
        img = np.array(img) / 255.0

        # Dummy detection (fast cloud)
        result = "Leaf Spot"
        confidence = 0.92

        msg = f"Disease: {result}\nConfidence: {confidence:.2f}"
        send_telegram(msg)

        return jsonify({
            "disease": result,
            "confidence": confidence
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# ================== RUN ==================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)