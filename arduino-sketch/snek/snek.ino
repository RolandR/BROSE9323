#include <TimeLib.h>
#include <BROSE9323.h>


int height = 16;
int width = 84;
int panelWidth = 28;
int fliptime = 250;

int bufferWidth = (width+7)/8;
int bufferSize = bufferWidth*height;

bool world[width*height];

signed char headX = int(width/2);
signed char headY = int(height/2);
signed char tailX = int(width/2);
signed char tailY = int(height/2)-1);

signed char foodX = width-10;
signed char foodY = 10;

char dir = 0;

world[headY*width+headX] = true;
world[tailY*width+tailX] = true;
world[foodY*width+foodX] = true;

BROSE9323 display(width, height, panelWidth, fliptime);

void setup() {
  
  display.begin();
  display.setDirect(true);

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
  
}

void loop() {
  
  display.drawPixel(headX, headY, 1);

  display.display();

  delay(1);
  
}
