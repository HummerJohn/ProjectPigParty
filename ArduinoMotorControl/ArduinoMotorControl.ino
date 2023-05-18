// AccelStepper.h look into this

const int ppsPin = 2;  // Pin number for the PPS signal
const int DirPin = 5;  // Pin Number for direction
const int EnaPin = 8;
const float DegreeConversion = 10000 / 360;
// const int encoderPinA = 3;
// const int encoderPinB = 4;

unsigned int ppsDelay = 0.0;  // Initial delay in seconds
unsigned int Direction = 0;
unsigned int Zeroing = 1;
volatile long FFPosPul = 0;
volatile long FFPosPul_OLD = 0;
volatile int FFPosDeg = 0;

void setup() {
  Serial.begin(115200);       // Set baud rate for serial communication
  pinMode(ppsPin, OUTPUT);  // Set pin mode for PPS signal
  pinMode(DirPin, OUTPUT);
  pinMode(EnaPin, OUTPUT);
  Serial.setTimeout(100);
  digitalWrite(EnaPin, LOW);
  digitalWrite(DirPin, LOW);
  // pinMode(encoderPinA, INPUT_PULLUP);
  // pinMode(encoderPinB, INPUT_PULLUP);
}

void loop() {
  if (Serial.available() > 0) {
    String inputString = Serial.readStringUntil('\n');  // Read the serial input until a newline character is received
    int commaIndex1 = inputString.indexOf(',');  // Find the index of the comma separator
    int commaIndex2 = inputString.indexOf(',', commaIndex1 + 1);

    if (commaIndex1 != -1 && commaIndex2 != -1) {
      String ppsString = inputString.substring(0, commaIndex1);   // Extract the float value string
      String DirString = inputString.substring(commaIndex1 + 1, commaIndex2);
      String ZeroString = inputString.substring(commaIndex2 + 1);
      
      ppsDelay = ppsString.toFloat();                            // Convert the float value string to a float
      Direction = DirString.toInt();                             // Convert the boolean value string to a boolean (0 or 1)
      Zeroing = ZeroString.toInt();

      digitalWrite(DirPin, Direction == 1 ? LOW : HIGH);
      digitalWrite(EnaPin, ppsDelay > 0 ? HIGH : LOW);
      
      if (Zeroing == 0) {
        FFPosDeg = 0;
        FFPosPul = 0;
      }
    }
  }

  if (ppsDelay > 0) {
    digitalWrite(ppsPin, HIGH);
    delayMicroseconds(ppsDelay);
    digitalWrite(ppsPin, LOW);
    delayMicroseconds(ppsDelay);
    FFPosPul += (Direction == 1) ? 1 : -1;
    if (((abs(FFPosPul) % round(DegreeConversion + (DegreeConversion * abs(FFPosDeg))) == 0) && (abs(FFPosPul) > abs(FFPosPul_OLD))) || 
        ((abs(FFPosPul) % round((DegreeConversion * abs(FFPosDeg)) - DegreeConversion) == 0) && (abs(FFPosPul) < abs(FFPosPul_OLD)))) {
      FFPosDeg += (Direction == 1) ? 1 : -1;

      if (FFPosDeg == 360) {
        FFPosDeg = 0;
        FFPosPul = 0;
      } else if (FFPosDeg == -1) {
        FFPosDeg = 359;
        FFPosPul = 9693;
      }
      FFPosPul_OLD = FFPosPul;
      Serial.println(FFPosDeg);
    }
  }
}