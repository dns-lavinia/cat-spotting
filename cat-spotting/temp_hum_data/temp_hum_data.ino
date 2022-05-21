/*************************************************** 
  This is an example for the SHT31-D Humidity & Temp Sensor

  Designed specifically to work with the SHT31-D sensor from Adafruit
  ----> https://www.adafruit.com/products/2857

  These sensors use I2C to communicate, 2 pins are required to  
  interface
 ****************************************************/
 
#include <Arduino.h>
#include <Wire.h>
#include "Adafruit_SHT31.h"

bool disableHeater = false;
uint8_t loopCnt = 0;

Adafruit_SHT31 sht31 = Adafruit_SHT31();

void setup() {
  Serial.begin(9600);

  while (!Serial)
    delay(10);    

  if (! sht31.begin(0x44)) { 
    Serial.println("Couldn't find SHT31");
    while (1) delay(1);
  }

  // make sure that the heater is disabled
  sht31.heater(disableHeater);
}


void loop() {
  float t = sht31.readTemperature();
  float h = sht31.readHumidity();

  if (! isnan(t)) {  // check if 'is not a number'
    Serial.print("temperature="); Serial.print(t); Serial.print(" ");
  } else { 
    Serial.println("Failed to read temperature");
  }
  
  if (! isnan(h)) {  // check if 'is not a number'
    Serial.print("humidity="); Serial.println(h);
  } else { 
    Serial.println("Failed to read humidity");
  }

  delay(1000);
}
