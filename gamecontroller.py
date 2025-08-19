import cv2
import pyautogui
import math
from HandTrackingmodule import HandDetector   # your class

cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.7)

# Keep track of states
w_pressed = False
clicking = False

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if lmList:
        # --- Forward movement (index finger up) ---
        if lmList[8][2] < lmList[6][2]:   # finger up
            if not w_pressed:             # only press once
                pyautogui.keyDown('w')
                w_pressed = True
        else:
            if w_pressed:                 # only release once
                pyautogui.keyUp('w')
                w_pressed = False

        # --- Click (thumb & index close) ---
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        length = math.hypot(x2 - x1, y2 - y1)

        if length < 30 and not clicking:
            pyautogui.mouseDown()
            clicking = True
        elif length >= 30 and clicking:
            pyautogui.mouseUp()
            clicking = False

    cv2.imshow("Game Controller", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
