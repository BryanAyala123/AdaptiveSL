import serial
import time

# Replace with the correct COM port and baud rate for your LCD connection
ARDUINO_PORT = 'COM3'  # Change to the correct port your USB device is connected to
BAUD_RATE = 9600

def connect_lcd():
    """Establish connection to the LCD via USB serial port"""
    try:
        ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Allow connection to stabilize
        print(f"Connected to LCD on {ARDUINO_PORT}")
        return ser
    except Exception as e:
        print(f"Failed to connect to LCD: {e}")
        return None

def send_to_lcd(ser, message):
    """Send message to LCD over serial"""
    if ser and ser.is_open:
        try:
            ser.write(f"{message}\n".encode())  # Send the message followed by a newline
            print(f"Sent to LCD: {message}")
        except Exception as e:
            print(f"Error sending to LCD: {e}")
    else:
        print(f"[SIMULATION] LCD Message: {message}")

def main():
    """Main function to test communication with the LCD"""
    lcd_connection = connect_lcd()
    
    if lcd_connection:
        # Send some test messages
        send_to_lcd(lcd_connection, "Hello World!")
        time.sleep(2)  # Simulate showing the message for 2 seconds
        
        send_to_lcd(lcd_connection, "Updated Message!")
        time.sleep(2)  # Simulate showing the updated message for 2 seconds
        
        # Send more messages as needed...
        send_to_lcd(lcd_connection, "Final Message")
        
        # Close the connection when done
        lcd_connection.close()
        print("Connection closed.")
    else:
        print("Could not connect to the LCD.")

if __name__ == "__main__":
    main()
