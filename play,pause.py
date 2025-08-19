import os
os.environ["GLOG_minloglevel"] = "3"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import cv2
import time
import mediapipe as mp
import HandTrackingmodule as htm
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pyautogui

# Webcam dimensions
wcam, hcam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wcam)
cap.set(4, hcam)

pTime = 0
detector = htm.HandDetector(detectionCon=0.7)

# Tap detection
tap_times_index = []   # taps for thumb + index
tap_times_middle = []  # taps for thumb + middle
tap_cooldown = 0.3     # seconds
last_tap_index = 0
last_tap_middle = 0

# Audio device setup
device = AudioUtilities.GetSpeakers()
interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Volume range
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]

vol = 0
volBar = 400  # Position for drawing the volume bar
volPer = 0


# ---------------- FUNCTION FOR PLAY/PAUSE ----------------
def check_play_pause(length_index, length_middle, cTime):
    global tap_times_index, tap_times_middle, last_tap_index, last_tap_middle

    # ---- Thumb + Index = Play ----
    if length_index < 35:
        if cTime - last_tap_index > tap_cooldown:
            tap_times_index.append(cTime)
            last_tap_index = cTime

    tap_times_index = [t for t in tap_times_index if time.time() - t < 1.2]

    if len(tap_times_index) == 2:
        pyautogui.press("playpause")  # Play
        print("▶️ Play")
        tap_times_index.clear()

    # ---- Thumb + Middle = Pause ----
    if length_middle < 35:
        if cTime - last_tap_middle > tap_cooldown:
            tap_times_middle.append(cTime)
            last_tap_middle = cTime

    tap_times_middle = [t for t in tap_times_middle if time.time() - t < 1.2]

    if len(tap_times_middle) == 2:
        pyautogui.press("playpause")  # Pause
        print("⏸️ Pause")
        tap_times_middle.clear()




while True:
    success, img = cap.read()
    if not success:
        continue

    cTime = time.time()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)



    if len(lmList) != 0:
        # Thumb tip = 4, Index tip = 8, Middle tip = 12
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        x3, y3 = lmList[12][1], lmList[12][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Draw circles & line between fingers
        cv2.circle(img, (x1, y1), 8, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 8, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, (x3, y3), 8, (255, 0, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.line(img, (x1, y1), (x3, y3), (255, 0, 0), 2)
        cv2.circle(img, (cx, cy), 8, (0, 0, 255), cv2.FILLED)

        # Length between fingers
        length_index = math.hypot(x2 - x1, y2 - y1)
        length_middle = math.hypot(x3 - x1, y3 - y1)

        # Convert length to volume range
        vol = np.interp(length_index, [50, 300], [minVol, maxVol])
        volBar = np.interp(length_index, [50, 300], [400, 150])  # Y-axis inverted
        volPer = np.interp(length_index, [50, 300], [0, 100])   # % for display

        # Set system volume
        volume.SetMasterVolumeLevel(vol, None)

        # If fingers very close, highlight
        if length_index  < 50:
            cv2.circle(img, (cx, cy), 10, (255, 255, 255), cv2.FILLED)

        # ---- CALL PLAY/PAUSE FUNCTION ----
        check_play_pause(length_index, length_middle, cTime)

    # Draw volume bar
    cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 255), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 255, 255), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 430), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if cTime != pTime else 0
    pTime = cTime
    cv2.putText(img, f"FPS: {int(fps)}", (40, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
