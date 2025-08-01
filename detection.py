import os
import torch
import numpy as np
from PIL import Image
from ultralytics import YOLO

# Load YOLOv8n-face model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'weights', 'yolov8n-face.pt')
yolo_model = YOLO(MODEL_PATH)

def detect_face_from_pil(pil_image):
    """
    Detects the largest face in a PIL image using YOLOv8n-face and returns a 160x160 PIL crop.
    Returns None if no face is detected.
    """
    try:
        # Convert to numpy array
        img_array = np.array(pil_image)

        # Run YOLOv8 detection
        results = yolo_model.predict(source=img_array, conf=0.5, verbose=False)

        if not results or len(results[0].boxes) == 0:
            return None

        # Get all bounding boxes
        boxes = results[0].boxes.xyxy.cpu().numpy()  # shape (n, 4) with [x1, y1, x2, y2]
        # Choose the largest face based on area
        biggest = max(boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))

        x1, y1, x2, y2 = map(int, biggest)
        cropped = pil_image.crop((x1, y1, x2, y2)).resize((160, 160))

        return cropped
    except Exception as e:
        print(f"[ERROR] Face detection failed: {str(e)}")
        return None
