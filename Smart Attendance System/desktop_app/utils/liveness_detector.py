import cv2
import numpy as np
import time

class LivenessDetector:
    def __init__(self):
        # Precise thresholds for digital screen rejection
        # Real faces in user's environment hit ~170-186. Screens hit ~180-184.
        # We increase to 195 to avoid false positives from natural facial features.
        self.MOIRE_THRESHOLD = 195.0 
        self.GLARE_THRESHOLD = 245 
        self.GLARE_RATIO_LIMIT = 0.12 
        
        # Texture Limits (Laplacian Variance)
        # User's camera is very sharp (500+). We increase MAX limit significantly.
        self.TEXTURE_VAR_MIN = 25.0    # Lower = too blurry (print)
        self.TEXTURE_VAR_MAX = 700.0   # Higher = digital grain/pixels (screen)
        self.SAT_LIMIT = 150.0         # Highly saturated "neon" colors of screens
        
    def detect_liveness(self, frame, face_box=None, landmarks=None):
        """
        Advanced sensor fusion to distinguish 3D human from 2D screen.
        """
        results_data = {
            'is_screen': False,
            'reason': "",
            'landmarks': landmarks,
            'pattern_val': 0,
            'laplacian_var': 0,
            'avg_sat': 0,
            'glare_ratio': 0
        }
        
        if face_box is None:
            return results_data

        x, y, w, h = map(int, face_box)
        x, y = max(0, x), max(0, y)
        face_roi = frame[y:y+h, x:x+w]
        
        if face_roi.size < 400:
            return results_data

        # 1. Frequency Analysis (FFT)
        is_pattern, pattern_val = self.analyze_frequency(face_roi)
        results_data['pattern_val'] = pattern_val
        
        # 2. Sharpness Analysis (Laplacian)
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        results_data['laplacian_var'] = laplacian_var
        
        # 3. Saturation (Screens have vibrant synthetic light)
        hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
        avg_sat = np.mean(hsv[:,:,1])
        results_data['avg_sat'] = avg_sat
        
        # 4. Glare Check
        _, thresh = cv2.threshold(gray, self.GLARE_THRESHOLD, 255, cv2.THRESH_BINARY)
        glare_ratio = np.count_nonzero(thresh) / thresh.size if thresh.size > 0 else 0
        results_data['glare_ratio'] = glare_ratio

        # --- Sensor Fusion Logic ---
        spoof_score = 0
        
        # Moire Pattern Check
        if pattern_val > self.MOIRE_THRESHOLD: 
            spoof_score += 2
        elif pattern_val > 175: # Potential screen pattern
            spoof_score += 1
            
        # Digital screens are either "too perfect" (sharp grid) or "too blurry"
        if laplacian_var > self.TEXTURE_VAR_MAX: 
            spoof_score += 1 # Potential digital pixel noise
        elif laplacian_var < self.TEXTURE_VAR_MIN:
            spoof_score += 1 # Likely low-res print
            
        # Screen glow vs Natural skin tone
        if avg_sat > self.SAT_LIMIT: 
            spoof_score += 1
            
        # Screen glass reflections
        if glare_ratio > self.GLARE_RATIO_LIMIT: 
            spoof_score += 1

        # Rejection Rule:
        # We only reject if Moire is strong OR if we have multiple weak indicators.
        if (pattern_val > 210) or (spoof_score >= 2):
            results_data['is_screen'] = True
            if pattern_val > self.MOIRE_THRESHOLD:
                results_data['reason'] = "Digital Screen Pattern detected"
            elif laplacian_var > self.TEXTURE_VAR_MAX:
                results_data['reason'] = "Digital Grain (Screen) detected"
            elif avg_sat > self.SAT_LIMIT:
                results_data['reason'] = "Synthetic Light/Screen Glow"
            else:
                results_data['reason'] = "Mobile Screen Spoof detected"
            
        return results_data

    def analyze_frequency(self, face_roi):
        """FFT analysis for digital screen grids"""
        try:
            gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            roi_resized = cv2.resize(gray, (128, 128))
            f = np.fft.fft2(roi_resized)
            fshift = np.fft.fftshift(f)
            magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)
            
            h_f, w_f = magnitude_spectrum.shape
            cy, cx = h_f // 2, w_f // 2
            
            # Mask natural facial features (Low/Mid Freq)
            mask_size = 28 # Slightly larger to hide more face detail
            magnitude_spectrum[cy-mask_size : cy+mask_size, cx-mask_size : cx+mask_size] = 0
            
            max_val = np.max(magnitude_spectrum)
            return (max_val > self.MOIRE_THRESHOLD), max_val
        except:
            return False, 0

    def get_movement_status(self, landmarks_history):
        """
        Calculates 3D head turning variance using Geometric Rigidity.
        Strict check to separate 2D tilts (rigid) from 3D turns (non-rigid).
        """
        if len(landmarks_history) < 15:
            return False
            
        history = np.array(landmarks_history) 
        var_total = np.sum(np.var(history, axis=0))
        
        # 1. Reject perfectly still images (photos)
        if var_total < 0.2: # Lowered to 0.2 for sublte movement
            return False

        # 2. Geometric Consistency Check
        # Ratio of Width (le-re) to Depth (mid-nose)
        le_x, le_y = history[:, 0], history[:, 1]
        re_x, re_y = history[:, 2], history[:, 3]
        n_x, n_y = history[:, 4], history[:, 5]
        
        eye_w = np.sqrt((le_x - re_x)**2 + (le_y - re_y)**2)
        mx, my = (le_x + re_x)/2, (le_y + re_y)/2
        nose_h = np.sqrt((n_x - mx)**2 + (n_y - my)**2)
        
        nose_h = np.where(nose_h == 0, 1, nose_h)
        ratio = eye_w / nose_h
        r_var = np.var(ratio)
        
        # Real 3D turns create non-proportional landmark shifts (depth variance)
        if r_var > 0.0008: # Balanced threshold
            return True
            
        return False
