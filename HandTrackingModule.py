import cv2  # Importing the OpenCV library
import mediapipe as mp  # Importing the Mediapipe library for hand tracking
import time  # Importing the time module

# Defining a class for hand detection and tracking
class handDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        # Constructor method to initialize parameters
        self.mode = mode  # Whether to detect static images or videos
        self.maxHands = maxHands  # Maximum number of hands to detect
        self.detectionCon = detectionCon  # Minimum confidence threshold for detection
        self.trackCon = trackCon  # Minimum confidence threshold for tracking
        
        # Creating instances of the Hand tracking module from Mediapipe
        self.mpHands = mp.solutions.hands
        # Initializing the Hand tracking module with specified parameters
        self.hands = self.mpHands.Hands(static_image_mode=self.mode,
                                        max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.trackCon)
        # Creating an instance of the drawing utilities module from Mediapipe
        self.mpDraw = mp.solutions.drawing_utils

    # Method to detect hands in an image
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Converting BGR image to RGB
        # Processing the RGB image to find hands
        self.results = self.hands.process(imgRGB)
        # Drawing landmarks and connections if draw is True
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img  # Returning the image with detected hands drawn

    # Method to find positions of landmarks on detected hands
    def findPosition(self, img, handNo=0, draw=True, color=(255, 0, 255), z_axis=False):
        lmList = []  # List to store landmark positions
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                if not z_axis:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])  # Appending landmark id and position to list
                else:
                    cx, cy, cz = int(lm.x * w), int(lm.y * h), round(lm.z, 3)
                    lmList.append([id, cx, cy, cz])  # Appending landmark id and 3D position to list

                if draw:
                    cv2.circle(img, (cx, cy), 5, color, cv2.FILLED)  # Drawing a circle at landmark position

        return lmList  # Returning the list of landmark positions

# Main function
def main():
    pTime = 0  # Previous time initialization for FPS calculation
    cap = cv2.VideoCapture(1)  # Capturing video from camera
    detector = handDetector(maxHands=1)  # Creating an instance of handDetector class
    while True:
        success, img = cap.read()  # Reading frame from camera
        if not success:
            break  # Break if frame not successfully read
        img = detector.findHands(img)  # Detecting hands in the frame
        lmList = detector.findPosition(img, z_axis=True, draw=False)  # Finding landmark positions
        if len(lmList) != 0:
            print(lmList[4])  # Printing position of specific landmark
        
        cTime = time.time()  # Current time for FPS calculation
        fps = 1 / (cTime - pTime)  # Calculating frames per second
        pTime = cTime  # Updating previous time

        # Displaying FPS on the image
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

        cv2.imshow("Image", img)  # Displaying the image with detected hands
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Waiting for 'q' key to exit the loop
            break
    cap.release()  # Releasing the video capture object
    cv2.destroyAllWindows()  # Closing all OpenCV windows

if __name__ == "__main__":
    main()  # Calling the main function if script is run directly




