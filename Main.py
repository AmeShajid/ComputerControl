import platform  # Import the platform module to access information about the platform (operating system)
import cv2  # Import the OpenCV library for image and video processing tasks
import time  # Import the time module for various time-related functions
import math  # Import the math module for mathematical functions and constants
import numpy as np  # Import NumPy library for numerical computing

# Import custom HandTrackingModule as htm
import HandTrackingModule as htm

# Import PyAutoGUI library for controlling the mouse and keyboard
import pyautogui

# Import Autopy library for simulating mouse and keyboard input
import autopy

# Check the platform (operating system) to conditionally import Windows-specific libraries
if platform.system() == "Windows":
    from ctypes import cast, POINTER  # Import necessary functions for Windows audio control
    from comtypes import CLSCTX_ALL  # Import necessary constant for Windows audio control
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # Import Windows audio control libraries

# Set the width and height of the camera input
wCam, hCam = 640, 480

# Initialize the camera object with index 0 (default camera)
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open video device.")
    exit()

# Set the resolution of the camera capture
cap.set(3, wCam)
cap.set(4, hCam)

# Initialize previous time variable for calculating FPS
pTime = 0

# Create an instance of the hand detection module
detector = htm.handDetector(maxHands=1, detectionCon=0.85, trackCon=0.8)

# Conditionally initialize Windows-specific audio control objects
if platform.system() == "Windows":
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volRange = volume.GetVolumeRange()

    # Set minimum and maximum volume levels
    minVol = -63
    maxVol = volRange[1]
    print(volRange)

# Initialize variables for hand gesture recognition and volume control
hmin = 50
hmax = 200
volBar = 400
volPer = 0
vol = 0
color = (0, 215, 255)

# Define the finger IDs used for hand gesture recognition
tipIds = [4, 8, 12, 16, 20]

# Initialize mode and active variables
mode = ''
active = 0

# Disable PyAutoGUI fail-safe to prevent unintentional termination
pyautogui.FAILSAFE = False

# Function to display text on the image
def putText(mode, loc=(250, 450), color=(0, 255, 255)):
    cv2.putText(img, str(mode), loc, cv2.FONT_HERSHEY_COMPLEX_SMALL, 3, color, 3)

# Main loop for capturing and processing camera frames
while True:
    # Read a frame from the camera
    success, img = cap.read()

    # Check if frame capture was successful
    if not success:
        print("Failed to capture image")
        break

    # Use the hand detection module to find hands in the frame
    img = detector.findHands(img)
    
    # Get the landmark positions of the detected hand(s)
    lmList = detector.findPosition(img, draw=False)

    # Initialize an empty list for storing finger states
    fingers = []

    # Check if any landmarks were detected
    if len(lmList) != 0:
        # Check if the index finger is extended
        if lmList[tipIds[0]][1] > lmList[tipIds[0 - 1]][1]:
            if lmList[tipIds[0]][1] >= lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        elif lmList[tipIds[0]][1] < lmList[tipIds[0 - 1]][1]:
            if lmList[tipIds[0]][1] <= lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)

        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        if (fingers == [0, 0, 0, 0, 0]) & (active == 0):
            mode = 'N'
        elif (fingers == [0, 1, 0, 0, 0] or fingers == [0, 1, 1, 0, 0]) & (active == 0):
            mode = 'Scroll'
            active = 1
        elif (fingers == [1, 1, 0, 0, 0]) & (active == 0):
            mode = 'Volume'
            active = 1
        elif (fingers == [1, 1, 1, 1, 1]) & (active == 0):
            mode = 'Cursor'
            active = 1

    if mode == 'Scroll':
        active = 1
        putText(mode)
        cv2.rectangle(img, (200, 410), (245, 460), (255, 255, 255), cv2.FILLED)
        if len(lmList) != 0:
            if fingers == [0, 1, 0, 0, 0]:
                putText(mode='U', loc=(200, 455), color=(0, 255, 0))
                pyautogui.scroll(300)
            if fingers == [0, 1, 1, 0, 0]:
                putText(mode='D', loc=(200, 455), color=(0, 0, 255))
                pyautogui.scroll(-300)
            elif fingers == [0, 0, 0, 0, 0]:
                active = 0
                mode = 'N'

    if mode == 'Volume' and platform.system() == "Windows":
        active = 1
        putText(mode)
        if len(lmList) != 0:
            if fingers[-1] == 1:
                active = 0
                mode = 'N'
                print(mode)
            else:
                x1, y1 = lmList[4][1], lmList[4][2]
                x2, y2 = lmList[8][1], lmList[8][2]
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                cv2.circle(img, (x1, y1), 10, color, cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, color, cv2.FILLED)

                cv2.line(img, (x1, y1), (x2, y2), color, 3)
                cv2.circle(img, (cx, cy), 8, color, cv2.FILLED)

                # Calculate the distance between thumb and index finger
                length = math.hypot(x2 - x1, y2 - y1)

                # Map the hand distance to volume level
                vol = np.interp(length, [hmin, hmax], [minVol, maxVol])
                volBar = np.interp(vol, [minVol, maxVol], [400, 150])
                volPer = np.interp(vol, [minVol, maxVol], [0, 100])

                # Print volume and set the system volume level
                print(vol)
                volume.SetMasterVolumeLevel(vol, None)

                # Adjust volume bar color and display percentage
                if length < 50:
                    cv2.circle(img, (cx, cy), 11, (0, 0, 255), cv2.FILLED)
                cv2.rectangle(img, (30, 150), (55, 400), (209, 206, 0), 3)
                cv2.rectangle(img, (30, int(volBar)), (55, 400), (215, 255, 127), cv2.FILLED)
                cv2.putText(img, f'{int(volPer)}%', (25, 430), cv2.FONT_HERSHEY_COMPLEX, 0.9, (209, 206, 0), 3)

    if mode == 'Cursor':
        active = 1
        putText(mode)
        cv2.rectangle(img, (90, 20), (620, 350), (255, 255, 255), 3)

        # Check if all fingers except thumb are closed
        if fingers[1:] == [0, 0, 0, 0]:
            active = 0
            mode = 'N'
            print(mode)
        else:
            if len(lmList) != 0:
                # Get the index finger position and map it to screen coordinates
                x1, y1 = lmList[8][1], lmList[8][2]
                w, h = pyautogui.size()
                X = int(np.interp(x1, [110, 620], [0, w - 1]))
                Y = int(np.interp(y1, [20, 350], [0, h - 1]))
                cv2.circle(img, (lmList[8][1], lmList[8][2]), 7, (255, 255))
                cv2.circle(img, (lmList[8][1], lmList[8][2]), 7, (255, 255, 255), cv2.FILLED)
                cv2.circle(img, (lmList[4][1], lmList[4][2]), 10, (0, 255, 0), cv2.FILLED)  # thumb

                # Adjust cursor coordinates to ensure it moves smoothly
                if X % 2 != 0:
                    X = X - X % 2
                if Y % 2 != 0:
                    Y = Y - Y % 2
                print(X, Y)

                # Move the cursor to the calculated screen coordinates
                pyautogui.moveTo(X, Y)

                # Check if thumb is open, then perform a mouse click
                if fingers[0] == 0:
                    cv2.circle(img, (lmList[4][1], lmList[4][2]), 10, (0, 0, 255), cv2.FILLED)  # thumb
                    pyautogui.click()

    # Calculate and display the FPS (Frames Per Second)
    cTime = time.time()
    fps = 1 / ((cTime + 0.01) - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS:{int(fps)}', (480, 50), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)

    # Display the processed image with overlays
    cv2.imshow('Hand LiveFeed', img)

    # Check for the 'q' key press to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break





















