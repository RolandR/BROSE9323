#include <TimeLib.h>
#include <BROSE9323.h>


int height = 16;
int width = 84;
int panelWidth = 28;
int fliptime = 400;

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
  display.setTextWrap(false);
  display.setDirect(true);
}

void loop() {
  for(int x = width; x >= 0; x--){
    int stripeWidth = width/6;
    for(int y = 0; y <= height; y++){
      display.drawPixel((x+y)%width+1, y, 1);
      display.drawPixel((x+y+stripeWidth)%width+1, y, 0);
      display.drawPixel((x+y+width/3)%width+1, y, 1);
      display.drawPixel((x+y+width/3+stripeWidth)%width+1, y, 0);
      display.drawPixel((x+y+2*width/3)%width+1, y, 1);
      display.drawPixel((x+y+2*width/3+stripeWidth)%width+1, y, 0);
    }
  }
  //ydisplay.display();
  delay(10);
}
