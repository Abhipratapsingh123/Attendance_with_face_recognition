import cv2
import numpy as np
import os

# Initialize LBPH Face Recognizer
face_recognizer = cv2.face.LBPHFaceRecognizer_create()

# Get all images and their respective IDs
faces, ids = [], []

uploads = "uploads"
for filename in os.listdir(uploads):
    if filename.startswith("user"):
        img_path = os.path.join(uploads, filename)
        image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

        if image is None:
            print(f"Skipping {img_path}: Unable to load image.")
            continue  # Skip invalid images

        # Resize images to ensure consistency
        image = cv2.resize(image, (100, 100))  # Resize 
        face_id = int(filename.split(".")[1])  # Extract ID from filename

        faces.append(image)
        ids.append(face_id)

# Train the recognizer
face_recognizer.train(np.asarray(faces, dtype='uint8'), np.array(ids))

# Create the "models" directory if it doesn't exist
models_dir = "models"
if not os.path.exists(models_dir):
    os.makedirs(models_dir)

# Save the trained model inside the "models" folder
model_path = os.path.join(models_dir, "lbph_classifier.yml")
face_recognizer.save(model_path)

print(f"Training complete. Model saved as '{model_path}'.")
