#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASSWORD";

WebServer server(80);

#define RELAY_PIN 5

void handleCracked() {
  digitalWrite(RELAY_PIN, HIGH);   // Activate reject motor
  delay(500);
  digitalWrite(RELAY_PIN, LOW);
  server.send(200, "text/plain", "Cracked Triggered");
}

void setup() {
  pinMode(RELAY_PIN, OUTPUT);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  server.on("/cracked", handleCracked);
  server.begin();
}

void loop() {
  server.handleClient();
}