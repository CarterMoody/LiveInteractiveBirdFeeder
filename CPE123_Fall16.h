
// Writing by Hugh Smith - 9/2016
//  version 4
//
// Timer, LED, Button and support functions 

#ifndef MYCLASSES4_H
#define MYCLASSES4_H

#include "Arduino.h"

// support functions 
void printLibVersion(Stream & aStream = Serial);
void setupMessage(const char * file, Stream & aStream = Serial);
template<typename T> void printPair(char * aString, T & aValue, int newLine = true);
void serialPrintf(const char * format, ...);
void serialPrintf(Stream & aStream, const char * format, ...);
void printVolts(int aPin, Stream & aStream = Serial);

// template must be in .h - known problem with ardruino preprocessor
template<typename T> void printPair(char * aString, T & aValue, int newLine)
 {  
	Serial.print(aString);
	 
	 if (newLine == true)
	 {
		 Serial.println(aValue);
	 }
	 else
	 {
		 Serial.print(aValue);
	 }
 }
 

// MSTimer enums
enum {MSTIMER_DONE, DELAYING};

class MSTimer {
 
 private:
  unsigned long msDuration;
  unsigned long start_time;
  int msDelayState;
  void reset(uint32_t ms_duration);
  
 public: 
  MSTimer();
  MSTimer(uint32_t ms_duration);
  void set(uint32_t ms_duration);
  unsigned long remaining();
  int done();

};

// Led enums 
enum {ON_BLINK, OFF_BLINK_SHORT, OFF_BLINK_LONG, BLINKING_OFF};

class Led {
  private:
    unsigned char pin;
	
    unsigned long durationOn;
	unsigned long shortDurationOff;
	unsigned long longDurationOff;
    int blinkState;
	int numRepeatBlinks;
	int repeatCount;
    MSTimer ledDelay;
		        
    // only used internally
	void initLed();
 
   public:
    Led(int ledPin);
	Led();
	void initPin(int ledPin);
    void on();
    void off();
    void update();
	void numberedBlinkOn(int repeatsOn = 2, uint32_t durationOn = 500, uint32_t shortDurationOff = 200, uint32_t longDurationOff = 1000);
    void blinkOn(unsigned long aDuration = 1000);

};


// Button enums
enum {PUSH_START, PUSH_WAITING};
enum {DUR_START, DUR_WAITING, DUR_TIME};

class Button
{
 
 private:
  int pin;
  
  // isPushed variables
  int pushState;
  MSTimer pushTimer;

  // duration variables
  int durState;
  unsigned long durStart;
  MSTimer durTimer;
  
 public:
  Button(int buttonPin);
  int wasPushed();
  int isPushed();
  unsigned long duration();
};

#endif

