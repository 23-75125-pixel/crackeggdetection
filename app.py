from flask import Flask, render_template, Response, jsonify
from flask_cors import CORS
import cv2
from ultralytics import YOLO
import threading
import os
import time
import numpy as np
from datetime import datetime
import requests
import serial

# ── Serial/Network Configuration ───────
arduino = None  # Initialize as None, connect later
try:
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    print("✅ Arduino connected")
except serial.SerialException:
    print("⚠️ Arduino not found - will continue without hardware")
except Exception as e:
    print(f"⚠️ Error connecting to Arduino: {e}")

ESP32_IP = "http://192.168.1.50/cracked"

def send_to_esp32(status):
    """Send status to ESP32 device"""
    try:
        if status == "cracked":
            requests.get(ESP32_IP, timeout=0.2)
    except Exception as e:
        print(f"⚠️ ESP32 communication error: {e}")

app = Flask(__name__)
CORS(app)

# ── Config ─────────────────────────────
MODEL_PATH = "/home/superjp/Desktop/crackeggdetection/best.pt"
FRAME_W = 640
FRAME_H = 480
TARGET_FPS = 30

# ── Global State ───────────────────────
camera = None
model = None
detection_active = False
camera_lock = threading.Lock()

stats = {
    "total_detections": 0,
    "good_eggs": 0,
    "cracked_eggs": 0,
    "detection_history": [],
    "fps": 0,
    "camera_status": "disconnected"
}

# ── Model ──────────────────────────────
def load_model():
    global model
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found:", MODEL_PATH)
        return False
    model = YOLO(MODEL_PATH)
    print("✅ Model loaded")
    return True


# ── Camera ─────────────────────────────
def init_camera(index=0):
    global camera

    with camera_lock:
        if camera:
            camera.release()

        cam = cv2.VideoCapture(index)
        if not cam.isOpened():
            stats["camera_status"] = "disconnected"
            print("❌ Camera not available")
            return False

        cam.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_W)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
        cam.set(cv2.CAP_PROP_FPS, TARGET_FPS)

        camera = cam
        stats["camera_status"] = "connected"
        print("✅ Camera connected")
        return True


def read_frame():
    with camera_lock:
        if camera and camera.isOpened():
            ret, frame = camera.read()
            if ret and frame is not None:
                return frame
    return None


# ── Create Blank Frame ─────────────────
def create_blank_frame(text="NO CAMERA"):
    frame = np.zeros((FRAME_H, FRAME_W, 3), dtype=np.uint8)
    cv2.putText(frame, text,
                (160, FRAME_H // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2)
    return frame


# ── Frame Generator ────────────────────
def generate_frames():
    global stats

    fps_count = 0
    fps_time = time.time()

    while True:
        frame = read_frame()

        if frame is None:
            stats["camera_status"] = "disconnected"
            blank = create_blank_frame()
            _, buffer = cv2.imencode(".jpg", blank)
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" +
                   buffer.tobytes() + b"\r\n")
            time.sleep(0.1)
            continue

        stats["camera_status"] = "connected"

        # ── FPS Calculation ──
        fps_count += 1
        if fps_count >= 30:
            elapsed = time.time() - fps_time
            stats["fps"] = int(fps_count / elapsed) if elapsed > 0 else 0
            fps_count = 0
            fps_time = time.time()

        # ── Detection ──
        if detection_active and model:
            try:
                results = model(frame, conf=0.25, verbose=False)

                for r in results:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])

                        x1, y1, x2, y2 = map(int, box.xyxy[0])

                        status = "GOOD" if cls == 0 else "CRACKED"
                        color = (0, 200, 0) if cls == 0 else (0, 0, 255)

                        # Draw bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                        label = f"{status} {conf:.0%}"

                        (w, h), _ = cv2.getTextSize(
                            label,
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            2
                        )

                        # Label background
                        cv2.rectangle(frame,
                                      (x1, y1 - h - 10),
                                      (x1 + w + 10, y1),
                                      color,
                                      -1)

                        # Label text
                        cv2.putText(frame,
                                    label,
                                    (x1 + 5, y1 - 5),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.6,
                                    (255, 255, 255),
                                    2)

                        # ── Update Stats ──
                        stats["total_detections"] += 1

                        if cls == 0:
                            stats["good_eggs"] += 1
                            status = "good"
                        else:
                            stats["cracked_eggs"] += 1
                            status = "cracked"
                            send_to_esp32(status)

                        stats["detection_history"].insert(0, {
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "status": status,
                            "confidence": f"{conf:.1%}"
                        })

                        if len(stats["detection_history"]) > 20:
                            stats["detection_history"].pop()

            except Exception as e:
                print("Detection error:", e)

        _, buffer = cv2.imencode(".jpg", frame)
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" +
               buffer.tobytes() + b"\r\n")


# ── Routes ─────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/start_detection", methods=["POST"])
def start_detection():
    global detection_active

    if not model:
        if not load_model():
            return jsonify({"success": False, "error": "Model not found"})

    if not camera:
        if not init_camera():
            return jsonify({"success": False, "error": "Camera not available"})

    detection_active = True
    return jsonify({"success": True})


@app.route("/stop_detection", methods=["POST"])
def stop_detection():
    global detection_active
    detection_active = False
    return jsonify({"success": True})


@app.route("/get_stats")
def get_stats():
    return jsonify(stats)


@app.route("/reset_stats", methods=["POST"])
def reset_stats():
    stats.update({
        "total_detections": 0,
        "good_eggs": 0,
        "cracked_eggs": 0,
        "detection_history": []
    })
    return jsonify({"success": True})


@app.route("/reconnect_camera", methods=["POST"])
def reconnect_camera():
    if init_camera():
        return jsonify({"success": True})
    return jsonify({"success": False})


# ── Main ───────────────────────────────
if __name__ == "__main__":
    print("🥚 EggGuard Pro starting...")
    load_model()
    init_camera()
    app.run(host="0.0.0.0", port=5000, threaded=True)