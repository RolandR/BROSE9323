#include <BROSE9323.h>

int height = 16;
int width = 84;
int panelWidth = 28;
int fliptime = 250;

int bufferWidth = (width+7)/8;
int bufferSize = bufferWidth*height;

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

  display.setCursor(2, 2);
  display.print(" reset");
  display.display();
  delay(500);
  
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

  Serial.readBytes(display._new_buffer, bufferSize);
  display.display();
  //Serial.println("waiting");
  
}
