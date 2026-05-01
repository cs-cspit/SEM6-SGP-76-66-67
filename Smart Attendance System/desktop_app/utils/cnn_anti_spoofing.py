import cv2
import numpy as np
import os

class CNNAntiSpoofing:
    def __init__(self, model_path="models/antispoof_model.onnx"):
        self.model_path = model_path
        self.net = None
        self.is_loaded = False
        self.load_model()
        
    def load_model(self):
        """Loads the MobileNetV2 ONNX model for Fast CPU Inference."""
        try:
            if os.path.exists(self.model_path):
                # Load ONNX model using OpenCV DNN
                self.net = cv2.dnn.readNetFromONNX(self.model_path)
                # Optimize for CPU
                self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
                self.is_loaded = True
                print(f"Anti-Spoofing Model loaded successfully from {self.model_path}")
            else:
                print(f"Warning: Anti-Spoofing Model not found at {self.model_path}")
                self.is_loaded = False
        except Exception as e:
            print(f"Error loading Anti-Spoofing Model: {e}")
            self.is_loaded = False
            
    def predict(self, frame, face_box):
        """
        Runs the cropped face through the CNN to detect spoofing.
        Input:
          frame: Original BGR frame from webcam
          face_box: (x, y, w, h) of the detected face
        Output:
          dict with 'label' (REAL/SPOOF) and 'confidence' (0-1)
        """
        # Default fallback response if model is missing or fails
        fallback_result = {'label': 'REAL', 'confidence': 1.0, 'error': True}
        
        if not self.is_loaded or face_box is None:
            return fallback_result
            
        x, y, w, h = map(int, face_box)
        x, y = max(0, x), max(0, y)
        
        # Ensure box is within frame boundaries
        hh, ww = frame.shape[:2]
        if x >= ww or y >= hh or w <= 0 or h <= 0:
            return fallback_result
            
        x2 = min(ww, x + w)
        y2 = min(hh, y + h)
        
        face_crop = frame[y:y2, x:x2]
        
        if face_crop.size == 0:
            return fallback_result
            
        try:
            # Prepare image for MobileNetV2
            # MobileNetV2 typically expects 224x224 RGB images, scaled to [-1, 1] or [0, 1]
            # using mean subtraction. Standard ImageNet means are (103.939, 116.779, 123.68) in BGR
            # Scalefactor = 1.0/127.5, mean = (127.5, 127.5, 127.5) is also common for [-1, 1]
            # Assuming standard [0, 1] scaling or similar depending on the specific model
            
            blob = cv2.dnn.blobFromImage(
                face_crop, 
                scalefactor=1.0/255.0, # Normalize to [0, 1]
                size=(224, 224), 
                mean=(0, 0, 0), 
                swapRB=True, # BGR to RGB
                crop=False
            )
            
            self.net.setInput(blob)
            
            # Forward pass
            preds = self.net.forward()
            
            # Assuming binary classification: [spoof_prob, real_prob]  (Adjust based on actual model output)
            # If model outputs a single sigmoid value, adjust logic accordingly.
            # Assuming output is [1, 2] shaped standard softmax/logits.
            
            preds = preds.flatten()
            
            if len(preds) >= 2:
                spoof_prob = float(preds[0])
                real_prob = float(preds[1])
            else:
                # If single output sigmoid (closer to 1 = REAL)
                real_prob = float(preds[0])
                spoof_prob = 1.0 - real_prob
                
            confidence = max(real_prob, spoof_prob)
            label = 'REAL' if real_prob > spoof_prob else 'SPOOF'
            
            return {
                'label': label,
                'confidence': confidence,
                'error': False,
                'real_prob': real_prob,
                'spoof_prob': spoof_prob
            }
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return fallback_result
