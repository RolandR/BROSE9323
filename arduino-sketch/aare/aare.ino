#include <TimeLib.h>
#include <BROSE9323.h>


int height = 16;
int width = 84;
int panelWidth = 28;
int fliptime = 250;

int bufferWidth = (width+7)/8;
int bufferSize = bufferWidth*height;

time_t timeOfLastSignal = now();
bool lostSignal = false;

BROSE9323 display(width, height, panelWidth, fliptime);

/*
 * UMLAUT:
 * Ä \x8E
 * ä \x84
 * Ö \x99
 * ö \x94
 * Ü \x9A
 * ü \x81
 * ß \xE0
 */
const char text[] = "Bitte nicht einsteigen";
const uint8_t textsize = 2;

void setup() {

  Serial.begin(9600);
  Serial.setTimeout(200);
  //while (!Serial);
  
  display.begin();
  display.setDirect(true);

  display.setTextSize(textsize);
  display.setTextWrap(false);
  display.setTextColor(1, 0);

  for(int x = 0; x <= width; x++){
    for(int y = 0; y <= height; y++){
      display.drawPixel(x, y, 1);
    }
  }
  for(int x = 0; x <= width; x++){
    for(int y = 0; y <= height; y++){
      display.drawPixel(x, y, 0);
    }
  }
  
  display.setDirect(false);
  Serial.println("GUTEN TAG");
}

void loop() {
  int delayTime = 0;

  int bytesRead = Serial.readBytes(display._new_buffer, bufferSize);
  if(bytesRead != 0){
    display.display();
    timeOfLastSignal = now();
    lostSignal = false;
  } else {
    if(!lostSignal){
      if(now() - timeOfLastSignal > 6*60){
        for(int x = 0; x <= width; x++){
          for(int y = 0; y <= height; y++){
            display.drawPixel(x, y, 0);
          }
        }
        display.setTextSize(1);
        display.setCursor(6, 0);
        display.print("z Raspi hets");
        display.setCursor(6, 8);
        display.print("gloubs putzt");
        display.display();
        lostSignal = true;
      }
    }
  }
}
