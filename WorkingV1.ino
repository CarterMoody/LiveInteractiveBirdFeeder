#include <RTClib.h>

#include <CPE123_Fall16.h>

// Just tests a motor, no other hardware needed

const int motor1A = 6;
const int motor1B = 7;

unsigned long real60M = 1000UL * 60 * 60;
int delay30S = 1000 * 30;
unsigned long adjusted60M = (real60M - delay30S) - 4000;
//int delay5S = 1000 * 5;

// Code from CircuitDigest to Read from Serial XBEE Communication
int received = 0;
int i;
/////

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  
  Serial.print("Begin: ");
  Serial.println(__FILE__);

   // Initalize the pins for output 
   pinMode(motor1A, OUTPUT);
   pinMode(motor1B, OUTPUT);

    // Stop the motor
   analogWrite(motor1A, 0);
   analogWrite(motor1B, 0);

   Serial.println("Staring motor testing");

   pinMode(LED_BUILTIN, OUTPUT);

   blinkInternal();

   feedBirds();
   
  }

// Runs motors for 2 seconds (2000ms)
void feedBirds(){
  analogWrite(motor1A, 0);
  analogWrite(motor1B, 250);
  
  delay(333);
 
  analogWrite(motor1A, 0);
  analogWrite(motor1B, 0);

}

void blinkInternal(){
  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
  delay(500);

  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
  delay(500);

  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
  delay(500);

}

void loop() {
  // put your main code here, to run repeatedly:
    if (Serial.available() > 0) {
      //blinkInternal();

      received = Serial.read();
      Serial.print(received);
      if (received == 'a'){

        feedBirds();
      }
    }
  
}
