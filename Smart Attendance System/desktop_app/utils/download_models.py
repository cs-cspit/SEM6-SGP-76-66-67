import os
import urllib.request
import sys

MODELS_DIR = os.path.join(os.getcwd(), "SmartAttendanceSystem", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

models = {
    "face_detection_yunet_2023mar.onnx": "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "face_recognition_sface_2021dec.onnx": "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx"
}

def download_file(url, path):
    print(f"Downloading {url} to {path}...")
    try:
        urllib.request.urlretrieve(url, path)
        print("Done.")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    for name, url in models.items():
        path = os.path.join(MODELS_DIR, name)
        if not os.path.exists(path):
            download_file(url, path)
        else:
            print(f"{name} already exists.")
