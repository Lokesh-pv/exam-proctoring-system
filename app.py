print("App started")
from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import glob
from datetime import datetime
import sqlite3
import cv2
import base64
import uuid
import numpy as np
from PIL import Image
import logging
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    static_folder='../frontend/static',
    template_folder='../frontend/templates'
)

# Import detection and recognition
from face_utils.detection import detect_face_from_pil
from face_utils.recognition import FaceRecognizer
face_recognizer = FaceRecognizer()

# Thread pool for batch processing
executor = ThreadPoolExecutor(max_workers=4)

# Folder paths
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'storage')
REFERENCE_IMAGES_DIR = os.path.join(UPLOAD_FOLDER, 'reference_images')
INCIDENTS_IMAGES_DIR = os.path.join(UPLOAD_FOLDER, 'incidents')
os.makedirs(REFERENCE_IMAGES_DIR, exist_ok=True)
os.makedirs(INCIDENTS_IMAGES_DIR, exist_ok=True)

def save_incident(student_id, image, incident_type):
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"{student_id}_{timestamp}_{str(uuid.uuid4())[:8]}.jpg"
        image_path = os.path.join(INCIDENTS_IMAGES_DIR, filename)
        cv2.imwrite(image_path, image)

        conn = sqlite3.connect('../database/incidents.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO incidents (student_id, timestamp, image_path, incident_type) VALUES (?, ?, ?, ?)',
            (student_id, datetime.now(), image_path, incident_type)
        )
        conn.commit()
        conn.close()
        return image_path
    except Exception as e:
        logger.error(f"Error saving incident: {str(e)}")
        return None

def process_single_frame(image_data, student_id, reference_embedding):
    try:
        header, encoded = image_data.split(',', 1)
        binary_data = base64.b64decode(encoded)
        image_np = np.frombuffer(binary_data, dtype=np.uint8)
        frame = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        face_crop = detect_face_from_pil(pil_image)

        if face_crop is None:
            logger.warning("No face detected in one of the frames")
            save_incident(student_id, frame, 'no_face')
            return {'status': 'error', 'message': 'No face detected'}

        current_embedding = face_recognizer.get_embedding(face_crop)

        distance = np.linalg.norm(reference_embedding - current_embedding)
        print(f"[INFO] Distance: {distance:.4f}")

        match = face_recognizer.compare_faces(reference_embedding, current_embedding, threshold=0.75)

        if not match:
            save_incident(student_id, frame, 'face_mismatch')
            return {'status': 'error', 'message': 'Face mismatch'}

        return {'status': 'success'}
    except Exception as e:
        logger.error(f"Frame processing error: {str(e)}")
        save_incident(student_id, frame, 'face_mismatch')
        return {'status': 'error', 'message': 'Processing error'}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/capture_reference_batch', methods=['POST'])
def capture_reference_batch():
    student_id = request.form.get('student_id')
    images = [
        request.form.get('image1'),
        request.form.get('image2'),
        request.form.get('image3')
    ]

    if not student_id or any(img is None for img in images):
        return jsonify({'error': 'Missing student_id or one or more images'}), 400

    try:
        for i, image_data in enumerate(images, start=1):
            header, encoded = image_data.split(',', 1)
            binary_data = base64.b64decode(encoded)
            image_np = np.frombuffer(binary_data, dtype=np.uint8)
            frame = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

            if frame is None:
                return jsonify({'error': f'Invalid image data for image {i}'}), 400

            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            face_crop = detect_face_from_pil(pil_image)

            if face_crop is None:
                return jsonify({'error': f'No face detected in image {i}'}), 400

            filename = f"{student_id}_{i}.jpg"
            reference_path = os.path.join(REFERENCE_IMAGES_DIR, filename)
            cv2.imwrite(reference_path, cv2.cvtColor(np.array(face_crop), cv2.COLOR_RGB2BGR))

        return jsonify({'success': True, 'message': 'All reference images saved successfully.'})
    except Exception as e:
        logger.error(f"Batch reference capture error: {str(e)}")
        return jsonify({'error': 'Failed to capture batch reference images'}), 500

@app.route('/api/batch_verify', methods=['POST'])
def batch_verify():
    student_id = request.form.get('student_id')
    image_data_list = request.form.getlist('images[]')

    if not student_id or not image_data_list:
        return jsonify({'error': 'Missing data'}), 400

    try:
        ref_paths = glob.glob(os.path.join(REFERENCE_IMAGES_DIR, f"{student_id}_*.jpg"))
        if not ref_paths:
            return jsonify({'error': 'Reference image(s) not found'}), 404

        embeddings = []
        for path in ref_paths:
            face = Image.open(path).convert('RGB')
            emb = face_recognizer.get_embedding(np.array(face))
            if emb is not None:
                embeddings.append(emb)

        if not embeddings:
            return jsonify({'error': 'No valid embeddings from reference images'}), 500

        reference_embedding = np.mean(embeddings, axis=0)

        futures = [
            executor.submit(process_single_frame, image_data, student_id, reference_embedding)
            for image_data in image_data_list
        ]

        results = [f.result() for f in futures]
        errors = [r for r in results if r['status'] == 'error']
        successes = [r for r in results if r['status'] == 'success']

        if len(errors) > len(successes):
            most_common_error = max(set([e['message'] for e in errors]), key=[e['message'] for e in errors].count)
            return jsonify({'status': 'error', 'message': most_common_error, 'detailed_results': results})

        return jsonify({'status': 'success', 'detailed_results': results})
    except Exception as e:
        logger.error(f"Batch verification error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/reference_images/<filename>')
def serve_reference_image(filename):
    return send_from_directory(REFERENCE_IMAGES_DIR, filename)

@app.route('/incident_images/<filename>')
def serve_incident_image(filename):
    return send_from_directory(INCIDENTS_IMAGES_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
