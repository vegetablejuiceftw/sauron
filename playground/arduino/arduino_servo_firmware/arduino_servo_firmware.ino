#include <Servo.h>

String buffer = "";    // string to hold input

Servo tilt;
Servo pan;

void setup() {
  tilt.attach(5);
  pan.attach(6);
  
  Serial.begin(9600);
  while (!Serial) {}
}

void loop() {
  // Read serial input:
  while (Serial.available() > 0) {
    int inChar = Serial.read();
    
    bool doPan = inChar == 'x';
    bool doTilt = inChar == 'y';
    
    if (isDigit(inChar)) {
      buffer += (char)inChar;
    }
    
    else if (doTilt || doPan) {
      Serial.print("Value:");
      Serial.println(buffer.toInt());
      Serial.print("String: ");
      Serial.println(buffer);
      // clear the string for new input:
      buffer = "";
      
      if (doTilt) {
        tilt.write(buffer.toInt());
      } else if (doPan) {
        tilt.write(buffer.toInt());
      }
    }
  }
}
