import sys
import cv2
import mediapipe as mp
import pyautogui
import math
import time
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

class GestureEngine(QThread):
    def __init__(self):
        super().__init__()
        self.current_action = "Left Click"
        self.tracking_mode = "Finger Wand (Index+Middle)"

    def run(self):
        # Initialize vision solutions
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.65, min_tracking_confidence=0.65)
        
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.65)

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        screen_w, screen_h = pyautogui.size()
        smooth_x, smooth_y = screen_w // 2, screen_h // 2
        smoothing = 0.30

        last_action_time = 0

        while cap.isOpened() and not self.isInterruptionRequested():
            success, frame = cap.read()
            if not success:
                time.sleep(0.01)
                continue

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            target_x, target_y = None, None
            current_time = time.time()

            # --- MODE A: EYE / HEAD TRACKING ---
            if self.tracking_mode == "Eye/Head Tracking":
                face_results = face_mesh.process(rgb_frame)
                if face_results.multi_face_landmarks:
                    face_landmarks = face_results.multi_face_landmarks[0]
                    # Landmark 4 is the tip of the nose (ideal for stable head pointer steering)
                    nose = face_landmarks.landmark[4]
                    target_x = int(nose.x * screen_w)
                    target_y = int(nose.y * screen_h)

            # --- MODE B: FINGER WAND TRACKING ---
            else:
                hand_results = hands.process(rgb_frame)
                if hand_results.multi_hand_landmarks:
                    hand_landmarks = hand_results.multi_hand_landmarks[0]
                    index_tip = hand_landmarks.landmark[8]
                    middle_tip = hand_landmarks.landmark[12]
                    thumb_tip = hand_landmarks.landmark[4]
                    wrist = hand_landmarks.landmark[0]

                    # Cursor Tracking via Midpoint
                    raw_mid_x = (index_tip.x + middle_tip.x) / 2
                    raw_mid_y = (index_tip.y + middle_tip.y) / 2
                    target_x = int(raw_mid_x * screen_w)
                    target_y = int(raw_mid_y * screen_h)

                    # Dynamic Trigger Math
                    idx_px = (int(index_tip.x * w), int(index_tip.y * h))
                    thmb_px = (int(thumb_tip.x * w), int(thumb_tip.y * h))
                    middle_px = (int(middle_tip.x * w), int(middle_tip.y * h))
                    
                    pinch_dist = math.igammac(0.5, (idx_px[0]-thmb_px[0])**2 + (idx_px[1]-thmb_px[1])**2) if hasattr(math, 'hypot') else math.sqrt((idx_px[0]-thmb_px[0])**2 + (idx_px[1]-thmb_px[1])**2)
                    
                    # 1. Action Trigger (Thumb Pinch)
                    if pinch_dist < 35 and (current_time - last_action_time > 0.4):
                        self.execute_mouse_action(self.current_action)
                        last_action_time = current_time

                    # 2. Volume Command Trigger (Spread hand out vs vertical movement)
                    # If index and middle open wide (Peace Sign) and go up/down
                    finger_separation = math.sqrt((idx_px[0]-middle_px[0])**2 + (idx_px[1]-middle_px[1])**2)
                    if finger_separation > 65 and (current_time - last_action_time > 0.25):
                        if index_tip.y < wrist.y - 0.2: # Hand raised high
                            pyautogui.press("volumeup")
                            last_action_time = current_time
                        elif index_tip.y > wrist.y - 0.05: # Hand dropped low
                            pyautogui.press("volumedown")
                            last_action_time = current_time

            # Apply interpolation filters if tracking data is live
            if target_x is not None and target_y is not None:
                smooth_x = (smooth_x * (1 - smoothing)) + (target_x * smoothing)
                smooth_y = (smooth_y * (1 - smoothing)) + (target_y * smoothing)
                pyautogui.moveTo(int(smooth_x), int(smooth_y))

            time.sleep(0.002)

        cap.release()

    def execute_mouse_action(self, action_name):
        if action_name == "Left Click": pyautogui.click()
        elif action_name == "Right Click": pyautogui.click(button='right')
        elif action_name == "Double Click": pyautogui.doubleClick()

class StarkWandUI(QWidget):
    def __init__(self):
        super().__init__()
        self.gesture_worker = GestureEngine()
        self.init_ui()
        self.gesture_worker.start()

    def init_ui(self):
        self.setWindowTitle("Stark Universal Engine")
        self.setGeometry(300, 300, 420, 220)
        self.setStyleSheet("background-color: #121214; color: #E1E1E6; font-family: Arial;")

        layout = QVBoxLayout()

        # Dynamic System Mode Selection
        mode_lbl = QLabel("Tracking Input Driver Mode:")
        mode_lbl.setStyleSheet("font-weight: bold; color: #00E676;")
        layout.addWidget(mode_lbl)
        
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.addItems(["Finger Wand (Index+Middle)", "Eye/Head Tracking"])
        self.mode_dropdown.setStyleSheet("background-color: #202024; padding: 5px;")
        self.mode_dropdown.currentTextChanged.connect(self.change_mode)
        layout.addWidget(self.mode_dropdown)

        # Trigger Actions Setup
        action_lbl = QLabel("Pinch Action Mapping:")
        action_lbl.setStyleSheet("margin-top: 10px;")
        layout.addWidget(action_lbl)

        self.action_dropdown = QComboBox()
        self.action_dropdown.addItems(["Left Click", "Right Click", "Double Click", "None"])
        self.action_dropdown.setStyleSheet("background-color: #202024; padding: 5px;")
        self.action_dropdown.currentTextChanged.connect(self.change_action)
        layout.addWidget(self.action_dropdown)

        help_lbl = QLabel("System Feature: Separate index/middle wide to engage Volume adjustments.")
        help_lbl.setStyleSheet("color: #7C7C8A; font-size: 10px; margin-top: 10px;")
        layout.addWidget(help_lbl)

        self.setLayout(layout)

    def change_mode(self, text):
        self.gesture_worker.tracking_mode = text

    def change_action(self, text):
        self.gesture_worker.current_action = text

    def closeEvent(self, event):
        self.gesture_worker.requestInterruption()
        self.gesture_worker.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StarkWandUI()
    window.show()
    sys.exit(app.exec())