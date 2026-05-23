#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Most I2C LCDs use 0x27. If display stays blank after flashing, try 0x3F.
LiquidCrystal_I2C lcd(0x27, 16, 2);

String row1    = "  LCD MONITOR   ";
String row2    = "  waiting...    ";
String incoming = "";

bool          dimming     = false;
bool          blState     = true;
unsigned long lastToggle  = 0;
const unsigned int DIM_MS = 5;  // 5ms toggle = 100Hz, 50% duty cycle

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print(row1);
  lcd.setCursor(0, 1);
  lcd.print(row2);
}

void updateLCD() {
  lcd.setCursor(0, 0);
  lcd.print(row1.substring(0, 16));
  lcd.setCursor(0, 1);
  lcd.print(row2.substring(0, 16));
}

void padTo16(String &s) {
  while (s.length() < 16) s += ' ';
}

void loop() {
  // software PWM for 50% dim
  if (dimming) {
    unsigned long now = millis();
    if (now - lastToggle >= DIM_MS) {
      lastToggle = now;
      blState = !blState;
      blState ? lcd.backlight() : lcd.noBacklight();
    }
  }

  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      if (incoming.startsWith("L1:")) {
        row1 = incoming.substring(3);
        padTo16(row1);
      } else if (incoming.startsWith("L2:")) {
        row2 = incoming.substring(3);
        padTo16(row2);
        updateLCD();
      } else if (incoming.startsWith("BL:")) {
        char v = incoming.charAt(3);
        if (v == '1') {
          dimming = false;
          blState = true;
          lcd.backlight();
        } else {
          dimming     = true;
          lastToggle  = millis();
        }
      }
      incoming = "";
    } else if (c != '\r') {
      incoming += c;
    }
  }
}
