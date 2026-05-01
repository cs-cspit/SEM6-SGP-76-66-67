import cv2
import os
import numpy as np
import pickle
import sys

class FaceRecognizer:
    def __init__(self):
        # Paths
        self.dataset_path = os.path.join(os.getcwd(), "dataset")
        if not os.path.exists(self.dataset_path):
             self.dataset_path = os.path.join(os.getcwd(), "..", "dataset")

        self.models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "models")
        # self.encodings_path removed (using DB)

        # Check for models
        self.yunet_path = os.path.join(self.models_dir, "face_detection_yunet_2023mar.onnx")
        self.sface_path = os.path.join(self.models_dir, "face_recognition_sface_2021dec.onnx")

        self.dl_available = False
        self.detector = None
        self.recognizer = None

        if os.path.exists(self.yunet_path) and os.path.exists(self.sface_path):
            try:
                self.detector = cv2.FaceDetectorYN.create(
                    self.yunet_path, "", (320, 320), 0.4, 0.3, 5000
                )
                self.recognizer = cv2.FaceRecognizerSF.create(self.sface_path, "")
                self.dl_available = True
                print("SUCCESS: YuNet & SFace Models Loaded.")
            except Exception as e:
                print(f"ERROR: Failed to load AI models: {e}")
        else:
            print("WARNING: ONNX Models not found. AI features will be limited.")

        # Data Store
        self.known_people = {} 
        
        # Inject Database
        from database.db import db
        self.db = db
        
        self.load_model()

    def enhance_image(self, img):
        """
        Req 1: Automatic brightness, CLAHE, Gamma, Noise Reduction
        """
        h, w = img.shape[:2]
        if w > 1280:
            scale = 1280 / w
            img = cv2.resize(img, (0,0), fx=scale, fy=scale)
        img = cv2.GaussianBlur(img, (3, 3), 0)
        gamma = 1.2
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        img = cv2.LUT(img, table)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l_eq = clahe.apply(l)
        lab_eq = cv2.merge((l_eq, a, b))
        img_final = cv2.cvtColor(lab_eq, cv2.COLOR_LAB2BGR)
        return img_final

    def check_face_quality(self, face_img):
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(100, (laplacian_var / 100.0) * 100)
        mean_brightness = np.mean(gray)
        brightness_score = 100 - (abs(128 - mean_brightness) * 0.8)
        overall_score = (0.6 * sharpness_score) + (0.4 * brightness_score)
        is_good = laplacian_var > 50 and 40 < mean_brightness < 220
        return overall_score, is_good

    def load_model(self):
        """
        Loads encodings from MongoDB.
        """
        print("Loading encodings from MongoDB...")
        try:
            self.known_people = self.db.get_all_encodings()
            print(f"Loaded Encodings for {len(self.known_people)} people.")
            return True
        except Exception as e:
            print(f"Error loading from DB: {e}")
            return False

    def train_model(self, progress_callback=None):
        """
        Req 3: Multi-Encoding Storage
        """
        if not self.dl_available:
            if progress_callback: progress_callback("Error: AI Models missing.")
            return False

        if progress_callback: progress_callback("Starting AI Training...")
        
        abs_dataset_path = os.path.abspath(self.dataset_path)
        if not os.path.exists(abs_dataset_path): return False
        
        student_dirs = [d for d in os.listdir(abs_dataset_path) if os.path.isdir(os.path.join(abs_dataset_path, d))]
        
        for student_id in student_dirs:
            if progress_callback: progress_callback(f"Learning {student_id}...")
            student_path = os.path.join(abs_dataset_path, student_id)
            
            student_encodings = []
            
            for filename in os.listdir(student_path):
                img_path = os.path.join(student_path, filename)
                img = cv2.imread(img_path)
                if img is None: continue
                
                # 1. Preprocess
                img = self.enhance_image(img)
                
                # 2. Detect
                h, w = img.shape[:2]
                self.detector.setInputSize((w, h))
                
                det_res = self.detector.detect(img)
                faces = det_res[1] if (det_res[1] is not None) else None
                
                if faces is not None:
                    # Sort by size, take largest
                    largest_face = max(faces, key=lambda f: f[2] * f[3])
                    
                    # 3. Align & Crop
                    aligned_face = self.recognizer.alignCrop(img, largest_face)
                    
                    # 4. Extract Encoding
                    feat = self.recognizer.feature(aligned_face)
                    student_encodings.append(feat)
            
            if student_encodings:
                # SAVE TO DB IMMEDIATELY
                self.db.update_student_encodings(student_id, student_encodings)
        
        # Reload to update local cache
        self.load_model()
        
        if progress_callback: progress_callback("Training Complete (Saved to DB).")
        return True

        return results

    def recognize_frame(self, frame):
        """
        Req 4 & 5: Dynamic Threshold & Confidence
        """
        results = []
        if not self.dl_available: return results 
        
        # 1. Preprocess Frame
        processed = self.enhance_image(frame)
        h, w = processed.shape[:2]
        
        # 2. Detect - INCREASED RESOLUTION for better small/angled face detection
        detector_h, detector_w = 640, 640
        self.detector.setInputSize((detector_w, detector_h))
        
        # Resize for detection (and map back coords later)
        # Actually YuNet handles scale if we just set InputSize and pass the image? 
        # No, InputSize must match strict image size if we resize.
        # But if we don't resize, we use (w, h). 
        # Using (w, h) is best for 640x480 webcam.
        self.detector.setInputSize((w, h))
        faces = self.detector.detect(processed)
        
        if faces[1] is None:
             return []
        
        faces = faces[1] 

        print(f"DEBUG: Found {len(faces)} faces.")

        for face in faces:
            x1, y1, w_f, h_f = map(int, face[:4])
            
            # Req 6: Quality - Relaxed for "different light" (trust enhancement)
            # x1, y1 = max(0, x1), max(0, y1)
            # face_crop = processed[y1:y1+h_f, x1:x1+w_f]
            # q_score, is_good = self.check_face_quality(face_crop)
            
            # 3. Align
            aligned_face = self.recognizer.alignCrop(processed, face)
            
            # 4. Feature Extraction
            feat = self.recognizer.feature(aligned_face)
            
            # --- TTA: Flip and Extract (Robustness for Angle) ---
            aligned_flipped = cv2.flip(aligned_face, 1)
            feat_flipped = self.recognizer.feature(aligned_flipped)

            # 5. Matching (Cosine Similarity) with Strict Threshold
            if not self.known_people:
                print("DEBUG: No known encodings loaded.")
                results.append({'id': None, 'conf': 0, 'box': (x1, y1, w_f, h_f)})
                continue

            best_id = None
            best_score = 0.0 
            
            # Iterate through known faces
            for uid, enc_list in self.known_people.items():
                for known_feat in enc_list:
                    # Match Original
                    score1 = self.recognizer.match(feat, known_feat, cv2.FaceRecognizerSF_FR_COSINE)
                    # Match Flipped (TTA)
                    score2 = self.recognizer.match(feat_flipped, known_feat, cv2.FaceRecognizerSF_FR_COSINE)
                    
                    max_score = max(score1, score2)
                    
                    if max_score > best_score:
                        best_score = max_score
                        best_id = uid
            
            # --- STRICT THRESHOLD CHECK ---
            # SFace Standard: 0.363
            # User experiencing false positives at 0.41-0.49.
            # Increasing to 0.55 for stricter matching.
            THRESHOLD = 0.55
            
            match_found = False
            final_conf = 0
            
            if best_score > THRESHOLD:
                match_found = True
                # Map Score to Confidence %
                # 0.55 -> 60%, 1.0 -> 100%
                normalized = (best_score - THRESHOLD) / (1.0 - THRESHOLD)
                final_conf = 60 + (normalized * 40)
                final_conf = min(100, final_conf)
                print(f"DEBUG: Match Found: {best_id} Score: {best_score:.3f} Conf: {final_conf:.1f}%")
            else:
                print(f"DEBUG: Unknown Face. Best Score: {best_score:.3f} (< {THRESHOLD})")
                best_id = None
                final_conf = 0
            
            results.append({
                'id': best_id,
                'conf': final_conf,
                'box': (x1, y1, w_f, h_f),
                'landmarks': face[4:14] 
            })
                
        return results

    # Compatibility shim if external code calls old methods
    def load_model_old(self): pass

    def encode_single_image(self, img):
        """
        Processes a single image and returns the face encoding (feature).
        Returns None if no face found or multiple faces (ambiguous), or list of encodings?
        For registration, we generally expect 1 face.
        """
        if img is None: return None
        if not self.dl_available: return None
        
        # 1. Try Detect on Original First (Sometimes enhancement hurts detection)
        h, w = img.shape[:2]
        self.detector.setInputSize((w, h))
        faces = self.detector.detect(img)
        
        # If no face found, try enhanced
        if faces[1] is None:
            print("DEBUG: No face in original, trying enhanced...")
            img_enhanced = self.enhance_image(img)
            self.detector.setInputSize((w, h))
            faces = self.detector.detect(img_enhanced)
            use_img = img_enhanced
        else:
            use_img = img
            
        if faces[1] is None:
            print("DEBUG: No face detected in image (even after enhancement).")
            return None
            
        # Get largest face
        largest_face = max(faces[1], key=lambda f: f[2] * f[3])
        
        # 3. Align
        aligned_face = self.recognizer.alignCrop(use_img, largest_face)
        
        # 4. Extract
        feat = self.recognizer.feature(aligned_face)
        return feat
