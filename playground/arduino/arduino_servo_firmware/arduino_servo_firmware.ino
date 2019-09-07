#include <Servo.h>

String buffer = "";    // string to hold input

Servo tilt;
Servo pan;

int tiltPos = 90;
int panPos = 90;

void setup() {
  tilt.attach(5);
  pan.attach(6);
  
  Serial.begin(115200);
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
      if (doTilt) {
        Serial.print("Tilt");
        tiltPos = buffer.toInt();
        Serial.println(tiltPos);
        tilt.write(tiltPos);
      } else if (doPan) {
        Serial.print("Turn");
        panPos = buffer.toInt();        
        Serial.println(panPos); 
        pan.write(panPos);
      }
      // clear the string for new input:
      buffer = "";
    }
  }
  pan.write(panPos);
  tilt.write(tiltPos);
  delay(15);
}
