#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Most I2C LCDs use 0x27. If display stays blank after flashing, try 0x3F.
LiquidCrystal_I2C lcd(0x27, 16, 2);

String row1     = "  LCD MONITOR   ";
String row2     = "  waiting...    ";
String incoming = "";

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print(row1);
  lcd.setCursor(0, 1);
  lcd.print(row2);
}

void padTo16(String &s) {
  while (s.length() < 16) s += ' ';
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      if (incoming.startsWith("L1:")) {
        row1 = incoming.substring(3);
        padTo16(row1);
        lcd.setCursor(0, 0);
        lcd.print(row1.substring(0, 16));
      } else if (incoming.startsWith("L2:")) {
        row2 = incoming.substring(3);
        padTo16(row2);
        lcd.setCursor(0, 1);
        lcd.print(row2.substring(0, 16));
      } else if (incoming.startsWith("BL:")) {
        char v = incoming.charAt(3);
        v == '1' ? lcd.backlight() : lcd.noBacklight();
      }
      incoming = "";
    } else if (c != '\r') {
      incoming += c;
    }
  }
}
