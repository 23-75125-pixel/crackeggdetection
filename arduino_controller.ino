#include <Arduino.h>

void setup() {
  Serial.begin(9600);
  pinMode(8, OUTPUT);  // Relay or motor control
}

void loop() {
  if (Serial.available()) {
    char signal = Serial.read();

    if (signal == 'C') {   // Cracked egg
      digitalWrite(8, HIGH);
      delay(500);
      digitalWrite(8, LOW);
    }
  }
}