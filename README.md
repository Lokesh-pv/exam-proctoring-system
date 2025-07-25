Exam Proctoring System
This project delivers a comprehensive AI-powered exam proctoring system, complete with both a robust backend and an interactive frontend. It leverages advanced computer vision techniques, including real-time face detection and recognition, to monitor students during online examinations and log potential incidents, ensuring academic integrity.

✨ Features
Real-time Face Detection: Utilizes YOLOv8n-face for accurate and efficient detection of faces in video frames from the student's webcam.

Advanced Face Recognition: Employs a FaceNet-based model (InceptionResnetV1) to generate and compare unique face embeddings, verifying student identity against registered reference images.

Reference Image Capture & Management: The frontend facilitates capturing multiple reference images of a student, which are then used by the backend to create a robust identity profile.

Continuous Identity Verification: Processes live video streams from the student's webcam to continuously monitor for identity mismatches or the absence of a face.

Automated Incident Logging: Automatically records potential proctoring incidents (e.g., "no face detected," "face mismatch") in an SQLite database for review.

Incident Image Storage: Saves images associated with detected incidents, providing visual evidence for later analysis.

Interactive Web Interface: A user-friendly frontend built with HTML, CSS, and JavaScript provides a seamless experience for students during exams and for administrators to manage proctoring.

RESTful API: The Flask backend exposes clear API endpoints for efficient communication with the frontend.

🚀 Technologies Used
Python

Flask: Web framework for building the backend API.

OpenCV (cv2): For image processing tasks.

NumPy: For numerical operations, especially with face embeddings.

Pillow (PIL): For image manipulation.

ultralytics (YOLOv8): For high-performance face detection.

facenet_pytorch: For implementing the FaceNet model for face recognition.

torch (PyTorch): The deep learning framework underlying FaceNet.

sqlite3 (built-in): For local incident database storage.

concurrent.futures.ThreadPoolExecutor: For efficient batch processing of frames.

Frontend

HTML5: For structuring the web interface (index.html).

CSS3: For styling the web application (styles.css).

JavaScript: For client-side logic, webcam interaction (camera.js), and managing UI alerts/messages (alerts.js).

⚙️ Setup and Installation
Follow these steps to get the system up and running on your local machine.

Prerequisites
Python 3.8+

pip (Python package installer)

An internet connection for initial model downloads (YOLOv8n-face weights and FaceNet vggface2 pretrained model).


Steps
Clone the Repository (or download the files):

git clone https://github.com/YourUsername/exam-proctoring-system.git
cd exam-proctoring-system

(If you're directly uploading, create the exam-proctoring-system folder and set up the structure manually as shown above.)

Create Directories:
Make sure the following directories exist:

mkdir -p backend/face_utils/weights
mkdir -p database
mkdir -p frontend/static
mkdir -p frontend/templates

Create a Virtual Environment (Recommended):

python -m venv venv

Activate the virtual environment:

Windows:

.\venv\Scripts\activate

macOS/Linux:

source venv/bin/activate

Install Dependencies:
Create a requirements.txt file in the root of your project (exam-proctoring-system/) with the following content:

Flask
opencv-python
numpy
Pillow
ultralytics
facenet_pytorch
torch

Then, install them:

pip install -r requirements.txt

Download YOLOv8n-face Model Weights:
Download the yolov8n-face.pt model from the Ultralytics GitHub repository and place it in the backend/face_utils/weights/ directory.
You can download it directly from: https://github.com/ultralytics/yolov8/releases/download/v8.0.0/yolov8n-face.pt

Initialize the Incident Database:
The app.py script expects an incidents table in database/incidents.db. You need to create this table manually once before running the application for the first time.
You can do this using a Python script or a SQLite browser:

Method 1: Using Python Script (Recommended)
Create a file named create_db.py in the database/ directory with the following content:

import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'incidents.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        image_path TEXT NOT NULL,
        incident_type TEXT NOT NULL
    )
''')
conn.commit()
conn.close()
print(f"Database '{db_path}' and table 'incidents' ensured to exist.")

Then run this script from the exam-proctoring-system/database/ directory:

python create_db.py

Run the Flask Backend:
Navigate to the backend/ directory and run app.py:

cd backend
python app.py

The server will start, usually on http://127.0.0.1:5000/.

💡 How to Use
Once the backend server is running, open your web browser and navigate to http://127.0.0.1:5000/.

The frontend index.html will load, and you can then:

Register Student Reference Images: The frontend will guide you to capture a series of images from your webcam. These images are sent to the backend's /api/capture_reference_batch endpoint to establish the student's identity.

Start Proctoring: After registration, the frontend will continuously capture webcam frames and send them in batches to the backend's /api/batch_verify endpoint.

Monitor Feedback: The frontend will display real-time feedback (e.g., "Face matched," "No face detected," "Face mismatch") and potentially log incidents for review.

Backend API Endpoints (for reference):
GET /: Renders the index.html from the frontend/templates directory.

POST /api/capture_reference_batch: To register a student by capturing multiple reference images for face recognition.

POST /api/batch_verify: To perform real-time face verification against registered reference images.

GET /reference_images/<filename>: Serves a specific reference image.

GET /incident_images/<filename>: Serves a specific incident image.
