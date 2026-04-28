from flask import Flask, request, render_template_string
import os
from PIL import Image
import numpy as np

app = Flask(__name__)

# ===== DATASET =====
DATASET_PATH = "dataset"

disease_map = {
    "1.jpg": "Healthy",
    "2.jpg": "Leaf Blight",
    "3.jpg": "Pest Attack",
    "4.jpg": "Powdery Mildew",
    "5.jpg": "Leaf Spot"
}

# ===== PROCESS IMAGE =====
def process_image(path):
    img = Image.open(path).resize((100, 100))
    return np.array(img).flatten()

# ===== MATCH =====
def get_disease(upload_path):
    uploaded = process_image(upload_path)

    best_score = float('inf')
    best_disease = "Unknown"

    for file in os.listdir(DATASET_PATH):
        dataset_path = os.path.join(DATASET_PATH, file)
        dataset_img = process_image(dataset_path)

        score = np.linalg.norm(uploaded - dataset_img)

        if score < best_score:
            best_score = score
            best_disease = disease_map.get(file, "Unknown")

    return best_disease

# ===== HOME (UPLOAD UI) =====
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
    path = "input.jpg"
    file.save(path)

    disease = get_disease(path)

    return f"<h2>🌿 Result: {disease}</h2>"

# ===== ESP32 UPLOAD =====
@app.route('/predict', methods=['POST'])
def predict():

    path = "input.jpg"

    with open(path, "wb") as f:
        f.write(request.data)

    disease = get_disease(path)

    return disease   # plain text for ESP32

# ===== HEALTH CHECK =====
@app.route('/status')
def status():
    return "Server Running"

# ===== RUN (RENDER) =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)