import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from pynput.keyboard import Key, Controller

# Set the desired width and height for the webcam screen
width, height = 640, 480  # Lower resolution for improved performance

# Open the webcam and set the width and height for capturing video frames
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Initialize the HandDetector with a confidence threshold and max no. of hands to detect (1 or 2)
detector = HandDetector(detectionCon=0.7, maxHands=1)

# Create a keyboard controller to simulate key presses
keyboard = Controller()

# Initialize the previous finger status as an invalid state
prev_fingers = None

# Variable to count the number of frames to skip for hand detection
skip_frames = 0

try:
    while True:
        # Read a frame from the webcam
        ret, img = cap.read()

        if not ret:
            break

        # Reduce the frame resolution for faster processing
        img = cv2.resize(img, (width, height))

        if skip_frames == 0:
            # Detect the hand in the frame using the HandDetector
            hands = detector.findHands(img, draw=False)

            # Reset skip_frames to its initial value after detection
            skip_frames = 5

        # Decrement skip_frames to skip the next few frames for hand detection
        skip_frames -= 1

        # Check if a hand is detected
        if hands:
            hand = hands[0]  # Get the first (and only) detected hand

            # Get the hand landmark points
            hand_landmarks = hand["lmList"]
            hand_np = np.array(hand_landmarks)

            # Calculate the finger tips y-coordinates
            fingertips_y = hand_np[[4, 8, 12, 16, 20]][:, 1]

            # Check which fingers are up
            fingers_up = fingertips_y < hand_landmarks[2][1]

            # Convert the finger status to a NumPy array
            fingers_np = np.array(fingers_up)

            # Check if the finger status has changed
            if prev_fingers is None or not np.array_equal(fingers_np, prev_fingers):
                prev_fingers = fingers_np

                # Only press the keyboard when the hand gesture changes
                if np.all(fingers_np):
                    # If all fingers are open, simulate pressing the right arrow key and release the left arrow key
                    keyboard.press(Key.right)
                    keyboard.release(Key.left)
                else:
                    # If all fingers are closed, simulate pressing the left arrow key and release the right arrow key
                    keyboard.press(Key.left)
                    keyboard.release(Key.right)

        else:
            prev_fingers = None
            # If no hand is detected, release both the left and right arrow keys
            keyboard.release(Key.left)
            keyboard.release(Key.right)

        # Show the image with hand gesture information
        cv2.imshow("hand_gesture_control", img)

        # Check for the "q" key press to exit the infinite loop and close the program
        if cv2.waitKey(1) == ord("q"):
            break

except Exception as e:
    print("Exception:", e)

finally:
    # Release the webcam and close the OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
