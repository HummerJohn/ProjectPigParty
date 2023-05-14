const int ppsPin = 2;  // Pin number for the PPS signal
unsigned int ppsDelay = 0.0;  // Initial delay in seconds

void setup() {
  Serial.begin(115200);       // Set baud rate for serial communication
  pinMode(ppsPin, OUTPUT);  // Set pin mode for PPS signal
  Serial.setTimeout(100);
}

void loop() {
  if (Serial.available() > 0) {
    String inputString = Serial.readStringUntil('\n');  // Read the serial input until a newline character is received
    ppsDelay = inputString.toFloat();                   // Convert the input string to a float value
    Serial.println(ppsDelay);
  }
  if (ppsDelay > 0) {
    // Calculate the delay in milliseconds for generating the PPS signal
    // unsigned long ppsDelayMs = ppsDelay * 1000;

    // Generate the PPS signal
    digitalWrite(ppsPin, HIGH);
    delayMicroseconds(ppsDelay);  // Adjust as needed
    digitalWrite(ppsPin, LOW);
    delayMicroseconds(ppsDelay);
  }
}
