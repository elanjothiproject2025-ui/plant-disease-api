from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

# ===== DISEASE MAP =====
disease_map = {
    "1": "Healthy",
    "2": "Leaf Blight",
    "3": "Pest Attack",
    "4": "Powdery Mildew",
    "5": "Leaf Spot"
}

# ===== HOME =====
@app.route('/')
def home():
    return render_template_string("""
    <html>
    <body style="text-align:center;">
    <h2>🌿 Plant Disease Detection</h2>

    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="image"><br><br>
        <input type="submit" value="Upload & Detect">
    </form>

    </body>
    </html>
    """)

# ===== LAPTOP UPLOAD =====
@app.route('/upload', methods=['POST'])
def upload():

    file = request.files['image']
    filename = file.filename   # 👈 important

    # extract number (1.jpg → 1)
    file_id = filename.split(".")[0]

    disease = disease_map.get(file_id, "Unknown")

    return f"<h2>🌿 Result: {disease}</h2>"

# ===== ESP32 ROUTE =====
@app.route('/predict', methods=['POST'])
def predict():

    # default demo (you can change manually if needed)
    file_id = "1"

    disease = disease_map.get(file_id, "Unknown")

    return disease

# ===== RUN =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)