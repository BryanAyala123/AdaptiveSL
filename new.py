import cv2
import mediapipe as mp
import serial
import time

# Arduino LCD Configuration
ARDUINO_PORT = 'COM3'  # Change to your Arduino's port
BAUD_RATE = 9600

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

def connect_arduino():
    """Establish connection to Arduino"""
    try:
        ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Allow connection to stabilize
        print(f"Connected to Arduino on {ARDUINO_PORT}")
        return ser
    except Exception as e:
        print(f"Failed to connect to Arduino: {e}")
        return None

def send_to_lcd(ser, message):
    """Send message to Arduino LCD"""
    if ser and ser.is_open:
        try:
            ser.write(f"{message}\n".encode())
            print(f"LCD Update: {message}")
        except Exception as e:
            print(f"LCD Send Error: {e}")
    else:
        print(f"[SIMULATION] LCD would show: {message}")

def is_fist(landmarks):
    """Detect fist gesture using hand landmarks"""
    # Finger tip indices (thumb, index, middle, ring, pinky)
    tip_ids = [4, 8, 12, 16, 20]
    
    # Check if fingertips are below their respective joints
    closed_fingers = 0
    for tip_id in tip_ids:
        tip_y = landmarks[tip_id].y
        joint_y = landmarks[tip_id - 1].y  # Previous landmark is the joint
        if tip_y > joint_y:  # Finger is closed
            closed_fingers += 1
    
    # Consider it a fist if at least 3 fingers are closed
    return closed_fingers >= 3

def main():
    # Initialize connections
    arduino = connect_arduino()
    send_to_lcd(arduino, "Initializing...")  # Initial message on the LCD
    cap = cv2.VideoCapture(0)
    
    last_state = None
    update_interval = 1  # Seconds between updates
    last_update = time.time()
    
    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                continue
                
            # Mirror and process frame
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            current_state = "No Hand"
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Get normalized landmarks
                    landmarks = hand_landmarks.landmark
                    current_state = "Fist" if is_fist(landmarks) else "Open Hand"
                    
                    # Draw hand landmarks (optional)
                    mp.solutions.drawing_utils.draw_landmarks(
                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Update LCD if state changed or periodically
            if current_state != last_state or (time.time() - last_update) > update_interval:
                send_to_lcd(arduino, current_state)  # Update LCD with current state
                last_state = current_state
                last_update = time.time()
            
            # Display status
            cv2.putText(frame, f"State: {current_state}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Fist Detection', frame)
            
            # Exit on 'q'
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
                
    finally:
        send_to_lcd(arduino, "System Off")  # Message when exiting
        cap.release()
        cv2.destroyAllWindows()
        if arduino:
            arduino.close()
        print("Program terminated")

if __name__ == "__main__":
    main()
