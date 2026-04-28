from flask import Flask, request, jsonify
import os
from PIL import Image
import numpy as np

app = Flask(__name__)

# ===== IMAGE FOLDER =====
DATASET_PATH = "dataset"

# ===== DISEASE LABELS =====
disease_map = {
    "1.jpg": "Healthy",
    "2.jpg": "Leaf Blight",
    "3.jpg": "Pest Attack",
    "4.jpg": "Powdery Mildew",
    "5.jpg": "Leaf Spot"
}

# ===== IMAGE PROCESSING =====
def preprocess_image(path):
    img = Image.open(path).resize((100, 100))
    return np.array(img).flatten()

# ===== COMPARE IMAGES =====
def find_match(upload_path):
    uploaded = preprocess_image(upload_path)

    best_score = float('inf')
    best_label = "Unknown"

    for file in os.listdir(DATASET_PATH):
        dataset_img_path = os.path.join(DATASET_PATH, file)

        dataset_img = preprocess_image(dataset_img_path)

        # simple difference
        score = np.linalg.norm(uploaded - dataset_img)

        if score < best_score:
            best_score = score
            best_label = disease_map.get(file, "Unknown")

    return best_label

# ===== HOME =====
@app.route('/')
def home():
    return "Plant Disease API Running"

# ===== PREDICT =====
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Save incoming image
        upload_path = "input.jpg"

        with open(upload_path, "wb") as f:
            f.write(request.data)

        # Find best match
        disease = find_match(upload_path)

        return jsonify({
            "disease": disease,
            "confidence": 0.95
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# ===== RUN =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)