import cv2
import mediapipe as mp
import serial
import time
import sys

# Arduino Setup
ARDUINO_PORT = 'COM3'  # Change to your Arduino port
BAUD_RATE = 9600

def connect_arduino():
    try:
        ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Allow connection to establish
        print(f"Connected to Arduino on {ARDUINO_PORT}")
        return ser
    except Exception as e:
        print(f"Arduino connection error: {e}")
        return None

def send_to_arduino(ser, message):
    if ser and ser.is_open:
        try:
            ser.write(f"{message}\n".encode())
            print(f"Sent: {message}")
        except Exception as e:
            print(f"Send error: {e}")
    else:
        print(f"[Simulation] Arduino would display: {message}")

# MediaPipe Hands Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_drawing = mp.solutions.drawing_utils

# Gesture Recognition Logic
def detect_gesture(landmarks):
    # Finger tip indices
    TIP_IDS = [4, 8, 12, 16, 20]
    
    # Get y-coordinates of fingertips and corresponding joints
    y_tips = [landmarks[i].y for i in TIP_IDS]
    y_joints = [
        landmarks[2].y,  # Thumb joint
        landmarks[5].y,  # Index joint
        landmarks[9].y,  # Middle joint
        landmarks[13].y, # Ring joint
        landmarks[17].y  # Pinky joint
    ]
    
    # Count closed fingers (tip below joint)
    closed_fingers = sum(1 for tip, joint in zip(y_tips, y_joints) if tip > joint)
    
    if closed_fingers == 0:
        return "Open"
    elif closed_fingers >= 3:
        return "Fist"
    return None

def main():
    # Initialize Arduino connection
    arduino = connect_arduino()
    send_to_arduino(arduino, "Initializing...")
    
    # Camera setup
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    last_gesture = None
    last_update = time.time()
    
    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # Flip and convert color
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = hands.process(rgb_frame)
            current_gesture = "No Hand"
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    mp_drawing.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    # Detect gesture
                    gesture = detect_gesture(hand_landmarks.landmark)
                    if gesture:
                        current_gesture = gesture
            
            # Update Arduino if gesture changed
            if current_gesture != last_gesture or (time.time() - last_update) > 5:
                send_to_arduino(arduino, current_gesture)
                last_gesture = current_gesture
                last_update = time.time()
            
            # Display status
            cv2.putText(frame, f"Gesture: {current_gesture}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Show preview
            cv2.imshow('Gesture Recognition', frame)
            
            # Exit on 'q'
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        send_to_arduino(arduino, "Shutdown")
        cap.release()
        cv2.destroyAllWindows()
        if arduino:
            arduino.close()
        print("System stopped")

if __name__ == "__main__":
    main()
