import cv2
import time
import mediapipe as mp
import HandTrackingmodule as htm
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Webcam dimensions
wcam, hcam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wcam)
cap.set(4, hcam)

pTime = 0
detector = htm.HandDetector(detectionCon=0.7)

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

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        # Thumb tip = 4, Index tip = 8
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # Draw circles & line between fingers
        cv2.circle(img, (x1, y1), 8, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 8, (0, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.circle(img, (cx, cy), 8, (0, 0, 255), cv2.FILLED)

        # Length between fingers
        length_index = math.hypot(x2 - x1, y2 - y1)

        # Convert length to volume range
        vol = np.interp(length_index, [50, 300], [minVol, maxVol])
        volBar = np.interp(length_index, [50, 300], [400, 150])  # Y-axis inverted
        volPer = np.interp(length_index, [50, 300], [0, 100])  # % for display

        # Set system volume
        volume.SetMasterVolumeLevel(vol, None)

        # If fingers very close, highlight
        if length_index < 50:
            cv2.circle(img, (cx, cy), 10, (255, 255, 255), cv2.FILLED)

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