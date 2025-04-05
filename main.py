import cv2
import time
import numpy as np

def process_frame(frame):
    """Applies background removal and blurring to the input frame."""
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Thresholding
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create mask
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, contours, -1, 255, cv2.FILLED)

    # Apply mask
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Optional: Smoothing
    blurred_result = cv2.GaussianBlur(result, (5, 5), 0)

    return blurred_result

def capture_with_timer(capture, interval):
    """Captures and processes frames at set time intervals."""
    start_time = time.time()
    frame_count = 0

    while True:
        ret, frame = capture.read()
        if not ret:
            print("Failed to grab frame.")
            break

        current_time = time.time()
        if current_time - start_time >= interval:
            processed = process_frame(frame)

            # Display original and processed side by side
            cv2.imshow('Original Frame', frame)
            cv2.imshow('Processed Frame', processed)

            # Save the processed frame if you want
            filename = f'processed_frame_{frame_count}.png'
            cv2.imwrite(filename, processed)
            print(f'Saved: {filename}')

            start_time = current_time
            frame_count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video source.")
        exit()

    capture_interval = 5  # every 2 seconds
    capture_with_timer(cap, capture_interval)
