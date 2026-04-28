from flask import Flask, request
import os
from PIL import Image
import numpy as np

app = Flask(__name__)

# ===== DATASET FOLDER =====
DATASET_PATH = "dataset"

# ===== DISEASE LABELS =====
disease_map = {
    "1.jpg": "Healthy",
    "2.jpg": "Leaf Blight",
    "3.jpg": "Pest Attack",
    "4.jpg": "Powdery Mildew",
    "5.jpg": "Leaf Spot"
}

# ===== IMAGE PROCESS =====
def process_image(path):
    img = Image.open(path).resize((100, 100))
    return np.array(img).flatten()

# ===== FIND BEST MATCH =====
def get_disease(upload_path):

    uploaded = process_image(upload_path)

    best_score = float('inf')
    best_disease = "Unknown"

    for file in os.listdir(DATASET_PATH):

        dataset_path = os.path.join(DATASET_PATH, file)

        dataset_img = process_image(dataset_path)

        # compare images
        score = np.linalg.norm(uploaded - dataset_img)

        if score < best_score:
            best_score = score
            best_disease = disease_map.get(file, "Unknown")

    return best_disease

# ===== HOME =====
@app.route('/')
def home():
    return "Plant Disease API Running"

# ===== PREDICT =====
@app.route('/predict', methods=['POST'])
def predict():

    try:
        # save incoming image
        upload_path = "input.jpg"

        with open(upload_path, "wb") as f:
            f.write(request.data)

        # detect disease
        disease = get_disease(upload_path)

        # ✅ RETURN ONLY TEXT (CLEAN OUTPUT)
        return disease

    except Exception as e:
        return "Error: " + str(e)

# ===== RUN =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)