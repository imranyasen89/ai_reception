"""
camera_detection.py
-------------------
DHQ Hospital Lodhran - AI Receptionist
Face Detection module using OpenCV.
Integrates with Streamlit's st.camera_input() for browser-based face detection.
"""

import os
import io
import tempfile

# ─── OpenCV Availability ─────────────────────────────────────────────────────
CAMERA_AVAILABLE = False
try:
    import cv2
    import numpy as np
    CAMERA_AVAILABLE = True
except ImportError:
    cv2 = None
    np = None


# ─── Configuration ────────────────────────────────────────────────────────────
FACE_CASCADE_PATH = None
MIN_FACE_SIZE = (80, 80)       # Minimum face size for detection
SCALE_FACTOR = 1.1              # Detection scale factor
MIN_NEIGHBORS = 5               # Min neighbors for detection confidence
BOX_COLOR = (0, 255, 120)      # Bounding box color (Green in BGR)
BOX_THICKNESS = 3               # Bounding box line thickness


def _get_cascade():
    """Load and return the Haar cascade classifier for face detection."""
    if not CAMERA_AVAILABLE:
        return None
    try:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        cascade = cv2.CascadeClassifier(cascade_path)
        if cascade.empty():
            return None
        return cascade
    except Exception as e:
        print(f"[Camera] Error loading cascade: {e}")
        return None


# ─── Core Detection ──────────────────────────────────────────────────────────
def detect_faces_from_bytes(image_bytes: bytes) -> dict:
    """
    Detect faces in an image from raw bytes (e.g., from st.camera_input).

    Args:
        image_bytes: Raw image bytes (JPEG/PNG from Streamlit camera)

    Returns:
        dict with:
            - detected (bool): True if at least one face found
            - face_count (int): Number of faces detected
            - faces (list): List of (x, y, w, h) tuples for each face
            - annotated_image (bytes): Image with bounding boxes drawn (JPEG bytes)
            - error (str): Error message if any
    """
    if not CAMERA_AVAILABLE:
        return {
            "detected": False,
            "face_count": 0,
            "faces": [],
            "annotated_image": image_bytes,
            "error": "OpenCV is not installed. Run: pip install opencv-python"
        }

    if not image_bytes:
        return {
            "detected": False,
            "face_count": 0,
            "faces": [],
            "annotated_image": None,
            "error": "No image data provided"
        }

    try:
        # Decode image from bytes
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return {
                "detected": False,
                "face_count": 0,
                "faces": [],
                "annotated_image": image_bytes,
                "error": "Could not decode image"
            }

        # Load face cascade
        face_cascade = _get_cascade()
        if face_cascade is None:
            return {
                "detected": False,
                "face_count": 0,
                "faces": [],
                "annotated_image": image_bytes,
                "error": "Face detection model not available"
            }

        # Convert to grayscale for detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Equalize histogram for better detection in varying lighting
        gray = cv2.equalizeHist(gray)

        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=SCALE_FACTOR,
            minNeighbors=MIN_NEIGHBORS,
            minSize=MIN_FACE_SIZE,
        )

        face_list = []
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                face_list.append((int(x), int(y), int(w), int(h)))

                # Draw bounding box
                cv2.rectangle(img, (x, y), (x + w, y + h), BOX_COLOR, BOX_THICKNESS)

                # Draw label
                label = "Face Detected"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                cv2.rectangle(
                    img,
                    (x, y - label_size[1] - 10),
                    (x + label_size[0] + 10, y),
                    BOX_COLOR, -1
                )
                cv2.putText(
                    img, label,
                    (x + 5, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 0, 0), 2
                )

        # Encode annotated image back to JPEG bytes
        _, annotated_bytes = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        annotated_bytes = annotated_bytes.tobytes()

        return {
            "detected": len(face_list) > 0,
            "face_count": len(face_list),
            "faces": face_list,
            "annotated_image": annotated_bytes,
            "error": ""
        }

    except Exception as e:
        return {
            "detected": False,
            "face_count": 0,
            "faces": [],
            "annotated_image": image_bytes,
            "error": f"Detection error: {str(e)}"
        }


def detect_from_camera_device(camera_index: int = 0) -> dict:
    """
    Capture a single frame from a camera device and detect faces.
    For kiosk use where the server has direct camera access.

    Args:
        camera_index: Camera device index (0 = default camera)

    Returns:
        Same dict format as detect_faces_from_bytes
    """
    if not CAMERA_AVAILABLE:
        return {
            "detected": False,
            "face_count": 0,
            "faces": [],
            "annotated_image": None,
            "error": "OpenCV is not installed"
        }

    try:
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            return {
                "detected": False,
                "face_count": 0,
                "faces": [],
                "annotated_image": None,
                "error": "Camera not available"
            }

        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            return {
                "detected": False,
                "face_count": 0,
                "faces": [],
                "annotated_image": None,
                "error": "Could not capture frame"
            }

        # Encode frame to bytes and use the main detection function
        _, img_bytes = cv2.imencode('.jpg', frame)
        return detect_faces_from_bytes(img_bytes.tobytes())

    except Exception as e:
        return {
            "detected": False,
            "face_count": 0,
            "faces": [],
            "annotated_image": None,
            "error": f"Camera error: {str(e)}"
        }


# ─── Utility ─────────────────────────────────────────────────────────────────
def is_opencv_installed() -> bool:
    """Check if OpenCV is installed."""
    return CAMERA_AVAILABLE


def is_camera_device_available(camera_index: int = 0) -> bool:
    """Check if a camera device is accessible."""
    if not CAMERA_AVAILABLE:
        return False
    try:
        cap = cv2.VideoCapture(camera_index)
        available = cap.isOpened()
        cap.release()
        return available
    except Exception:
        return False
