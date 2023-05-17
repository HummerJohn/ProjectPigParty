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

// volatile long pulse;
// volatile bool pinB, pinA, dir;

void setup() {
  Serial.begin(115200);       // Set baud rate for serial communication
  pinMode(ppsPin, OUTPUT);  // Set pin mode for PPS signal
  pinMode(DirPin, OUTPUT);
  pinMode(EnaPin, OUTPUT);
  Serial.flush();
  Serial.setTimeout(100);
  digitalWrite(EnaPin, LOW);
  digitalWrite(DirPin, LOW);
  // pinMode(encoderPinA, INPUT_PULLUP);
  // pinMode(encoderPinB, INPUT_PULLUP);

  // encoder pin on interrupt 0 (pin 2)
  // attachInterrupt(1, readEncoder, CHANGE);
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

      if (Direction == 1) {
        digitalWrite(DirPin, LOW);
      } else {
        digitalWrite(DirPin, HIGH);
      }
      if (ppsDelay > 0) {
        digitalWrite(EnaPin, HIGH);
      } else {
        digitalWrite(EnaPin, LOW);
      }
      if (Zeroing == 0) {
        FFPosDeg = 0;
        FFPosPul = 0;
        
      }
    }
  }
  if (ppsDelay > 0) {
    // Calculate the delay in milliseconds for generating the PPS signal
    // unsigned long ppsDelayMs = ppsDelay * 1000;

    // Generate the PPS signal
    digitalWrite(ppsPin, HIGH);
    delayMicroseconds(ppsDelay);  // Adjust as needed
    digitalWrite(ppsPin, LOW);
    delayMicroseconds(ppsDelay);
    if (Direction == 1) {
      FFPosPul++;
    } else {
      FFPosPul--;
    }
    if (((abs(FFPosPul) % round(DegreeConversion + (DegreeConversion * abs(FFPosDeg))) == 0) && (abs(FFPosPul) > abs(FFPosPul_OLD))) || 
        ((abs(FFPosPul) % round((DegreeConversion * abs(FFPosDeg)) - DegreeConversion) == 0) && (abs(FFPosPul) < abs(FFPosPul_OLD)))) {
      if (Direction == 1) {
        FFPosDeg++;
      } else {
        FFPosDeg--;
      }
      // if (FFPosDeg == 359) { Serial.println(FFPosPul);}

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

// void readEncoder() {
//   pinA = bitRead(PIND,encoderPinA);
//   pinB = bitRead(PIND,encoderPinB);
//   // dir = pinA ^ pinB;          // if pinA & pinB are the same
//   // dir ? --pulse : ++pulse;    // dir is CW, else CCW
//   if (Direction == 1) {
//     pulse++;
//   } else {
//     pulse--;
//   }  // if ((dir == Direction) and (yoloDir == 0)) {
//   //   Serial.println("directionfuck");
//   //   yoloDir = 1;
//   // }
// }