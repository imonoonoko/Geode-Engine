# senses.py
import threading
import queue
import time
import numpy as np
import mss
import os
import src.dna.config as config

# Phase 6.2: Visual Cortex Dependencies
import cv2
try:
    from ultralytics import YOLO
    _YOLO_AVAILABLE = True
except ImportError:
    print("⚠️ YOLOv8 not found. Visual Cortex will be limited.")
    _YOLO_AVAILABLE = False


# ==========================================
# 👁️ Retina (Foveated Vision)
# Center: High Res (YOLO) | Peripheral: Low Res (Motion/Color)
# ==========================================
class Retina:
    def __init__(self):
        self.prev_peripheral_gray = None
        self.prev_grids = [[None for _ in range(config.RETINA_MOTION_GRID_COLS)] for _ in range(config.RETINA_MOTION_GRID_ROWS)]
        
        # Fovea Settings
        self.fovea_size = 640 # Focus Area
        self.model = None
        self._model_loaded = False

    def _ensure_model(self):
        if not self._model_loaded and _YOLO_AVAILABLE:
            try:
                print("👁️ Lazy Loading YOLOv8 Nano (Foveated Vision)...")
                self.model = YOLO("yolov8n.pt") 
                self._model_loaded = True
            except Exception as e:
                print(f"⚠️ YOLO Load Error: {e}")
                self._model_loaded = True # Prevent retry spam

    def watch(self, sct, char_x, char_y, do_inference=True):
        """
        Foveated Vision Processing
        char_x, char_y: Focus Center (Character Position)
        do_inference: If False, skip YOLO (heavy) and only do Peripheral
        """
        self._ensure_model()
        
        # 1. Capture Full Screen (Raw)
        monitor = sct.monitors[1]
        # sct.grab returns MSS ScreenShot. 
        # Convert to Numpy/OpenCV
        full_frame = np.array(sct.grab(monitor))
        # Remove Alpha to get BGR
        full_frame = cv2.cvtColor(full_frame, cv2.COLOR_BGRA2BGR)
        
        h, w = full_frame.shape[:2]

        # --- 【Peripheral (周辺視野)】: Atmosphere & Motion ---
        # Resize to 10% (High Speed)
        small_frame = cv2.resize(full_frame, (0,0), fx=0.1, fy=0.1)
        peripheral_data = self._process_peripheral(small_frame)

        # --- 【Fovea (中心窩)】: Detail Object Recognition ---
        fovea_tags = []
        if self.model and do_inference:
            # Clamp crop area
            x1 = max(0, int(char_x - self.fovea_size / 2))
            y1 = max(0, int(char_y - self.fovea_size / 2))
            x2 = min(w, int(char_x + self.fovea_size / 2))
            y2 = min(h, int(char_y + self.fovea_size / 2))
            
            # Crop
            fovea_frame = full_frame[y1:y2, x1:x2]
            
            if fovea_frame.size > 0:
                 # YOLO Inference on small crop
                 results = self.model(fovea_frame, verbose=False, conf=0.5)
                 for r in results:
                     for box in r.boxes:
                         cls_name = self.model.names[int(box.cls)]
                         fovea_tags.append(cls_name)
                         
        return {
            "peripheral": peripheral_data,
            "fovea": list(set(fovea_tags)) # Unique tags
        }

    def _process_peripheral(self, frame):
        """ Analyze Atmosphere (Color/Bright) and Motion on low-res frame """
        # 1. Atmosphere (Replaces old analyze_atmosphere)
        # Calculate color means
        b, g, r = np.mean(frame[:, :, 0]), np.mean(frame[:, :, 1]), np.mean(frame[:, :, 2])
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        
        # 2. Motion Detection (Directional)
        motion_score = 0.0
        motion_grid = [[0.0 for _ in range(config.RETINA_MOTION_GRID_COLS)] for _ in range(config.RETINA_MOTION_GRID_ROWS)]
        
        # Blur for stability
        gray_blur = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.prev_peripheral_gray is not None:
             delta = cv2.absdiff(self.prev_peripheral_gray, gray_blur)
             thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
             
             # Global Motion Score
             motion_score = np.sum(thresh > 0) / (frame.shape[0] * frame.shape[1])
             motion_score = min(1.0, motion_score * 5.0) # Sensitivity boost
             
             # Grid Motion (3x3) - Lightweight on small frame
             h, w = thresh.shape
             cell_h = h // config.RETINA_MOTION_GRID_ROWS
             cell_w = w // config.RETINA_MOTION_GRID_COLS
             
             for gy in range(config.RETINA_MOTION_GRID_ROWS):
                 for gx in range(config.RETINA_MOTION_GRID_COLS):
                     y1, y2 = gy * cell_h, (gy + 1) * cell_h
                     x1, x2 = gx * cell_w, (gx + 1) * cell_w
                     # Count active pixels in cell
                     cell_sum = np.sum(thresh[y1:y2, x1:x2] > 0)
                     cell_area = (x2-x1) * (y2-y1)
                     if cell_area > 0:
                         motion_grid[gy][gx] = min(1.0, (cell_sum / cell_area) * 5.0)

        self.prev_peripheral_gray = gray_blur

        # 3. Construct Concept/Env Data (Compatible with Brain)
        effect = {}
        effect['color'] = (int(r), int(g), int(b))
        effect['motion_grid'] = motion_grid # Pass grid for body control logic
        
        # Logic from old analyze_atmosphere
        contrast = np.std(gray)
        if brightness < 40:
            if contrast > 20:
                effect['concept'] = 'Intellectual'
                effect['geo_target'] = 'North_High' 
            else:
                effect['concept'] = 'Void'
                effect['geo_target'] = 'Valley'
        elif brightness > 220:
            effect['concept'] = 'Bright'
            effect['geo_target'] = 'Peak'
        elif r > g + 30 and r > b + 30:
            effect['concept'] = 'Hot'
            effect['geo_target'] = 'South'
        elif b > r + 30 and b > g + 30:
            effect['concept'] = 'Cold'
            effect['geo_target'] = 'North'
        else:
            effect['concept'] = 'Normal'
            effect['geo_target'] = 'Center'

        if brightness > 180:
            effect['photosynthesis_rate'] = min(1.0, (brightness - 180) / 75.0)
        else:
            effect['photosynthesis_rate'] = 0.0
            
        # Add basic sensory data
        effect["視覚:赤"] = r / 255.0
        effect["視覚:緑"] = g / 255.0
        effect["視覚:青"] = b / 255.0
        effect["視覚:明"] = brightness / 255.0
        effect["視覚:動"] = motion_score
        
        return effect


# ==========================================
# 📡 KanameSenses (Asynchronous Manager)
# ==========================================
class KanameSenses:
    def __init__(self):
        print("👁️ Initializing Kaname Senses (Foveated)...")
        self.retina = Retina()
        self.is_active = True
        
        # Data Queues (Thread-safe communication)
        self.queue_global_vision = queue.Queue(maxsize=1) 
        self.queue_atmosphere = queue.Queue(maxsize=1)
        self.queue_grid_motion = queue.Queue(maxsize=1) # Kept for compatibility if needed
        
        self.focus_pos = (config.DEFAULT_X + 150, config.DEFAULT_Y + 150)
        self.focus_lock = threading.Lock()
        
        # Phase 28: Predictive Attention
        self.current_expectation = None # Target tag (e.g. "cup")
        
        # Phase 6.3 Optimization
        self.frame_counter = 0
        
        # Phase 6: Last vision data for AttentionManager
        self.last_vision_data = None
        
        # Start Sense Thread
        self.thread = threading.Thread(target=self._sense_loop, daemon=True)
        self.thread.start()

    def update_focus(self, x, y):
        """ Update the Fovea center (called from Body/Main) """
        with self.focus_lock:
            self.focus_pos = (x, y)

    def set_expectation(self, tag):
        """ Phase 28: Top-Down Attention Control """
        print(f"👁️ Attention: Looking for '{tag}'...")
        self.current_expectation = tag

    def _sense_loop(self):
        """ Dedicated thread for sensory processing """
        with mss.mss() as sct: 
            while self.is_active:
                start_time = time.time()
                
                # Get current focus
                with self.focus_lock:
                    fx, fy = self.focus_pos
                
                # Watch (Foveated) - One pass
                try:
                    # FRAME CONTROL (Phase 6.3 Optimization)
                    # Peripheral: 10 FPS (Check every frame of this loop)
                    # Fovea (YOLO): 2 FPS (Check every 5th frame)
                    self.frame_counter += 1
                    
                    # Phase 28: Active Inquiry (Look harder if expecting something)
                    freq_divider = 5
                    if self.current_expectation:
                        freq_divider = 2 # Check more often (5 FPS)
                        
                    do_fovea = (self.frame_counter % freq_divider == 0)
                    
                    vision_data = self.retina.watch(sct, fx, fy, do_inference=do_fovea)
                    
                    # Phase 6: Store for AttentionManager
                    self.last_vision_data = vision_data
                    
                    # 1. Peripheral -> Atmosphere & Grid Motion
                    p_data = vision_data["peripheral"]
                    try: self.queue_atmosphere.put_nowait(p_data)
                    except queue.Full: pass
                    
                    if "motion_grid" in p_data:
                         try: self.queue_grid_motion.put_nowait(p_data["motion_grid"])
                         except queue.Full: pass
                    
                    # 2. Fovea -> Objects (Only when inference ran)
                    if do_fovea:
                        f_tags = vision_data["fovea"]
                        if f_tags:
                             # Check Expectation Match
                             if self.current_expectation and self.current_expectation in f_tags:
                                 print(f"✨ FOUND IT! Saw '{self.current_expectation}'.")
                                 self.current_expectation = None # Satisfaction
                                 
                             v_stimulus = {
                               "type": "objects",
                               "tags": f_tags,
                               "timestamp": time.time()
                             }
                             try: self.queue_global_vision.put_nowait(v_stimulus)
                             except queue.Full: 
                                 try:
                                     self.queue_global_vision.get_nowait()
                                     self.queue_global_vision.put_nowait(v_stimulus)
                                 except: pass
                    
                except Exception as e:
                    print(f"⚠️ Sense Loop Error: {e}")
                    # traceback.print_exc() # Disable verbose trace to save log space
                    time.sleep(2.0) # Backoff to prevent log flood
                    continue # Skip timing logic

                elapsed = time.time() - start_time
                # Target: 10 FPS for Peripheral (Motion Awareness)
                # Sleep enough to hit ~0.1s total loop time
                time.sleep(max(0.01, 0.1 - elapsed))

    def request_local_vision(self, region):
        pass # Deprecated in Foveated Vision

    def get_global_vision(self):
        if not self.queue_global_vision.empty():
            return self.queue_global_vision.get()
        return None

    def get_local_vision(self):
        return None 

    def get_atmosphere(self):
        if not self.queue_atmosphere.empty():
            return self.queue_atmosphere.get()
        return None
        
    def get_grid_motion(self):
        # Return empty or None
        if not self.queue_grid_motion.empty():
            return self.queue_grid_motion.get()
        return None

    def stop(self):
        self.is_active = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)
