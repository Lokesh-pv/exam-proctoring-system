let video = document.getElementById('video');
let captureGuide = document.getElementById('captureGuide');
let previewImages = document.getElementById('previewImages');
let logList = document.getElementById('logList');

let recaptureBtn = document.getElementById('recaptureBtn');
let nextCaptureBtn = document.getElementById('nextCaptureBtn');
let saveBtn = document.getElementById('saveBtn');
let startExamBtn = document.getElementById('startExamBtn');
let stopExamBtn = document.getElementById('stopExamBtn');
let studentIdInput = document.getElementById('studentIdInput');
let alertModal = document.getElementById('alertModal');

let referenceImages = [];
let captureStage = 0;
let monitoringInterval = null;
const capturePrompts = [
    "Align your face in the center",
    "Turn your face to the left",
    "Turn your face to the right"
];

// Start webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
        nextCaptureBtn.disabled = false;
        recaptureBtn.disabled = false;
    })
    .catch(err => {
        console.error("Camera access denied:", err);
        alertModal.style.display = 'flex';
    });

// Capture a frame from the webcam
function captureFrame() {
    let canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    let ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg');
}

// Recapture current stage
// Full recapture logic
recaptureBtn.onclick = () => {
    referenceImages = [];
    captureStage = 0;

    previewImages.innerHTML = '';
    captureGuide.innerText = capturePrompts[0];

    nextCaptureBtn.disabled = false;
    saveBtn.disabled = true;

};
// Next capture
nextCaptureBtn.onclick = () => {
    if (!studentIdInput.value.trim()) {
        alert("Please enter your Student ID.");
        return;
    }

    if (captureStage < 3) {
        referenceImages[captureStage] = captureFrame();
        captureStage++;
        showPreview();

        if (captureStage < 3) {
            captureGuide.innerText = capturePrompts[captureStage];
        }

        if (captureStage === 3) {
            nextCaptureBtn.disabled = true;
            saveBtn.disabled = false;
        }
    }
};

// Preview thumbnails
function showPreview() {
    previewImages.innerHTML = '';
    referenceImages.forEach(dataUrl => {
        let img = document.createElement('img');
        img.src = dataUrl;
        previewImages.appendChild(img);
    });
}

// Save reference images
saveBtn.onclick = () => {
    const studentId = studentIdInput.value.trim();
    if (!studentId) {
        alert("Student ID is required.");
        return;
    }

    if (referenceImages.length !== 3) {
        alert("Please capture all 3 reference images.");
        return;
    }

    const formData = new FormData();
    formData.append("student_id", studentId);
    formData.append("image1", referenceImages[0]);
    formData.append("image2", referenceImages[1]);
    formData.append("image3", referenceImages[2]);

    fetch('/api/capture_reference_batch', {
        method: 'POST',
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert("✅ Reference images saved successfully!");
                startExamBtn.disabled = false;
            } else {
                alert("❌ Failed to save reference images: " + (data.error || data.message));
            }
        })
        .catch(err => {
            console.error("Upload error:", err);
            alert("Server error occurred.");
        });
};

// Start monitoring on exam start
startExamBtn.onclick = () => {
    const studentId = studentIdInput.value.trim();
    if (!studentId) {
        alert("Student ID is required.");
        return;
    }

    alert("🟢 Monitoring started...");
    startExamBtn.disabled = true;
    stopExamBtn.disabled = false;

    monitoringInterval = setInterval(() => {
        captureAndSendBatch(studentId);
    }, 5000); // every 5 seconds
};

// Stop monitoring
stopExamBtn.onclick = () => {
    if (monitoringInterval) {
        clearInterval(monitoringInterval);
        monitoringInterval = null;
        addToLog(`[${new Date().toLocaleTimeString()}] ⛔ Monitoring stopped.`);
        alert("🛑 Monitoring stopped.");
    }
    startExamBtn.disabled = false;
    stopExamBtn.disabled = true;
};

function captureAndSendBatch(studentId) {
    let images = [];
    let frameCount = 0;
    let captureInterval = setInterval(() => {
        images.push(captureFrame());
        frameCount++;
        if (frameCount >= 10) {
            clearInterval(captureInterval);
            sendBatchToServer(studentId, images);
        }
    }, 250); // 1 FPS (250 ms)
}

function sendBatchToServer(studentId, images) {
    const formData = new FormData();
    formData.append("student_id", studentId);
    images.forEach((img, i) => {
        formData.append("images[]", img);
    });

    fetch('/api/batch_verify', {
        method: 'POST',
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === "error") {
                addToLog(`[${new Date().toLocaleTimeString()}] ⚠️ ${data.message}`);
            }
        })
        .catch(err => {
            console.error("Verification error:", err);
            addToLog(`[${new Date().toLocaleTimeString()}] ❌ Server error`);
        });
}

// Append logs to UI
function addToLog(message) {
    let li = document.createElement('li');
    li.textContent = message;
    logList.appendChild(li);
}
