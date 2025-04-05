/*
  LiquidCrystal Library - Blink
*/

// include the library code:
#include <LiquidCrystal.h>

// initialize the library with your specific pin connections
const int rs = 6, rw = 5, en = 9, d4 = 3, d5 = 12, d6 = 11, d7 = 10;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);
// Note: R/W pin (rw) is not included in the constructor but should be connected to GND
// If you want to control R/W, you'd need a different constructor

void setup() {
  // Connect R/W pin to GND if not controlling it through code
  pinMode(rw, OUTPUT);
  digitalWrite(rw, LOW);
  
  // set up the LCD's number of columns and rows:
  lcd.begin(16, 2);
  // Print a message to the LCD.
  lcd.print("HELLO WORLD");
}

void loop() {
  // Turn off the blinking cursor:
  lcd.noBlink();
  delay(3000);
  // Turn on the blinking cursor:
  lcd.blink();
  delay(3000);
}
