#include <Arduino.h>
#include <Servo.h>
#include <CRC16.h>

const int LED_GREEN = 4;
const int LED_BLUE = 5;
const int SERVO_PIN = 6;

Servo myServo;
CRC16 crc;

void setup() {
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE, OUTPUT);
  myServo.attach(SERVO_PIN);
  Serial.begin(9600);

  // Initialize the CRC object with custom parameters
  crc.setPolynome(0x8005);
  crc.setInitial(0x0000);
  crc.setXorOut(0x0000);
  crc.setReverseIn(true);
  crc.setReverseOut(true);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    Serial.print("Full command received: ");  // Print the full command for debugging
    Serial.println(command);

    if (verifyCRC(command)) {
      handleCommand(command);
    } else {
      Serial.println("ERROR: CRC Mismatch");
    }
  }
}
bool verifyCRC(String command) {
  int lastDashIndex = command.lastIndexOf('-');
  if (lastDashIndex == -1) {
    Serial.println("No CRC found");
    return false;
  }

  // Extract CRC from the last segment after the last dash
  String crcValueStr = command.substring(lastDashIndex + 1);
  command = command.substring(0, lastDashIndex);  // Remove CRC from the command

  Serial.print("Command without CRC: ");
  Serial.println(command);
  Serial.print("Received CRC: ");
  Serial.println(crcValueStr);

  // Convert CRC string to integer
  uint16_t crcValue = (uint16_t)strtol(crcValueStr.c_str(), nullptr, 16);

  // Restart the CRC calculation
  crc.restart();
  for (int i = 0; i < command.length(); i++) {
    crc.add(command[i]);
  }
  uint16_t computedCRC = crc.calc();

  Serial.print("Computed CRC: ");
  Serial.println(computedCRC, HEX);

  // Compare computed CRC with received CRC
  return computedCRC == crcValue;
}
void handleCommand(String command) {
  if (command.startsWith("green-on")) {
    digitalWrite(LED_GREEN, HIGH);
    Serial.println("GREEN LED ON");
  } else if (command.startsWith("blue-on")) {
    digitalWrite(LED_BLUE, HIGH);
    Serial.println("BLUE LED ON");
  } else if (command.startsWith("green-off")) {
    digitalWrite(LED_GREEN, LOW);
    Serial.println("GREEN LED OFF");
  } else if (command.startsWith("blue-off")) {
    digitalWrite(LED_BLUE, LOW);
    Serial.println("BLUE LED OFF");
  } else if (command.startsWith("servo-")) {
    int pos = command.substring(6).toInt();
    myServo.write(pos);
    Serial.print("SERVO POSITION SET TO: ");
    Serial.println(pos);
  } else {
    Serial.println("INVALID COMMAND RECEIVED");
  }
}
