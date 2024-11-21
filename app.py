from flask import Flask, jsonify
import cv2
from pyzbar.pyzbar import decode
import threading
import time

app = Flask(__name__)

camera_active = False
qr_data = None

def start_camera():
    global qr_data, camera_active

    camera = cv2.VideoCapture(0)
    camera.set(3, 640)  
    camera.set(4, 480) 
    camera_active = True

    while camera_active:
        success, frame = camera.read()
        if not success:
            print("Failed to capture frame")
            qr_data = {"error": "Failed to capture frame"}
            break

        decoded_objects = decode(frame)
        if decoded_objects:
            for obj in decoded_objects:
                qr_data = {
                    "type": obj.type,
                    "data": obj.data.decode("utf-8")
                }
                print(f"Detected QR Code: {qr_data}") 
                camera_active = False  
                break

        time.sleep(0.1)  

    camera.release()

@app.route("/scan", methods=["GET"])
def scan():
    """
    API endpoint to scan a QR code and return the result immediately.
    """
    global qr_data, camera_active

    if camera_active:
        return jsonify({"message": "Camera is already active"}), 400

    qr_data = None
    scanner_thread = threading.Thread(target=start_camera)
    scanner_thread.start()

    scanner_thread.join()

    if qr_data:
        return jsonify(qr_data), 200
    else:
        return jsonify({"message": "No QR code detected"}), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)