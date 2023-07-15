#include <BROSE9323.h>

int height = 16;
int width = 84;
int panelWidth = 28;
int fliptime = 200;

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
  Serial.println("waiting");
  
  /*for (int16_t x = display.width(); x > -((int16_t) strlen(text) * textsize * 6); x--) {
    display.setCursor(x, 2);
    display.print(text);
    display.display();
    delay(20);
  }*/

  /*display.setCursor(2, 2);
  display.print("Flipdot");
  display.display();
  delay(2000);

  for(int x = 0; x <= width; x++){
    for(int y = 0; y <= height; y++){
      display.drawPixel(x, y, 0);
    }
  }

  delay(2000);*/

  /*for(int x = width; x >= 0; x--){
    int stripeWidth = width/6;
    for(int y = 0; y <= height; y++){
      display.drawPixel((x+y)%width+1, y, 1);
      display.drawPixel((x+y+stripeWidth)%width+1, y, 0);
      display.drawPixel((x+y+width/3)%width+1, y, 1);
      display.drawPixel((x+y+width/3+stripeWidth)%width+1, y, 0);
      display.drawPixel((x+y+2*width/3)%width+1, y, 1);
      display.drawPixel((x+y+2*width/3+stripeWidth)%width+1, y, 0);
    }
  }*/

  /*for(int y = 0; y <= height; y++){
    for(int x = 0; x <= width; x++){
      display.drawPixel(x, y, 1);
    }
  }
  for(int x = 0; x <= width; x++){
    for(int y = 0; y <= height; y++){
      display.drawPixel(x, y, 0);
    }
  }*/

  /*for(int y = 0; y <= height; y++){
    for(int x = 0; x <= width; x++){
      display.drawPixel(x, y, 1);
    }
  }
  for(int x = 0; x <= width; x++){
    for(int y = 0; y <= height; y++){
      display.drawPixel(x, y, 0);
    }
  }
  for(int y = height; y >= 0; y--){
    for(int x = 0; x <= width; x++){
      display.drawPixel(x, y, 1);
    }
  }
  for(int x = width; x >= 0; x--){
    for(int y = 0; y <= height; y++){
      display.drawPixel(x, y, 0);
    }
  }*/
  
  /*display.fillScreen(0);
  display.display();
  delay(200);
  display.fillScreen(1);
  display.display();
  delay(200);*/
  
}
