#include <TimeLib.h>
#include <BROSE9323.h>


int height = 16;
int width = 84;
int panelWidth = 28;
int fliptime = 250;

int bufferWidth = (width+7)/8;
int bufferSize = bufferWidth*height;

float posX = width/2;
float posY = height/2;

float vectorX = 1.0;
float vectorY = -2.0;
float speed = 20.0;

int lastTime = micros();

float paddle1Pos = width/2;
float paddle2Pos = width/2;
int paddle1Width = 6.0;
int paddle2Width = 6.0;

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

  lastTime = micros();
}

void loop() {
  int timeSinceLastTime = micros()-lastTime;
  lastTime = micros();

  display.drawPixel(int(posX-0.5), int(posY-0.5), 0);
  display.drawPixel(int(posX+0.5), int(posY-0.5), 0);
  display.drawPixel(int(posX-0.5), int(posY+0.5), 0);
  display.drawPixel(int(posX+0.5), int(posY+0.5), 0);

  for(int i = 0; i < paddle1Width; i++){
    display.drawPixel(int(paddle1Pos-paddle1Width/2+i), 0, 0);
  }
  for(int i = 0; i < paddle2Width; i++){
    display.drawPixel(int(paddle2Pos-paddle2Width/2+i), height-1, 0);
  }

  posX = posX + vectorX*(timeSinceLastTime/1000000.0)*speed;
  posY = posY + vectorY*(timeSinceLastTime/1000000.0)*speed;

  //vectorY = vectorY + 4*(timeSinceLastTime/1000000.0);

  if(posX < 0.5){
    vectorX = vectorX*(-1.0);
    posX = 0.5;
  } else if(posX > width-0.5){
    vectorX = vectorX*(-1.0);
    posX = width-0.5;
  }

  if(posY < 1.5){
    vectorY = vectorY*(-1.0);
    posY = 1.5;
  } else if(posY > height-1.5){
    vectorY = vectorY*(-0.8);
    posY = height-1.5;
  }

  paddle1Pos = posX;
  if(paddle1Pos < paddle1Width/2){
    paddle1Pos = paddle1Width/2;
  } else if(paddle1Pos > width-paddle1Width/2){
    paddle1Pos = width-paddle1Width/2;
  }

  paddle2Pos = posX;
  if(paddle2Pos < paddle2Width/2){
    paddle2Pos = paddle2Width/2;
  } else if(paddle2Pos > width-paddle2Width/2){
    paddle2Pos = width-paddle2Width/2;
  }

  for(int i = 0; i < paddle1Width; i++){
    display.drawPixel(int(paddle1Pos-paddle1Width/2+i), 0, 1);
  }
  for(int i = 0; i < paddle2Width; i++){
    display.drawPixel(int(paddle2Pos-paddle2Width/2+i), height-1, 1);
  }

  display.drawPixel(int(posX-0.5), int(posY-0.5), 1);
  display.drawPixel(int(posX+0.5), int(posY-0.5), 1);
  display.drawPixel(int(posX-0.5), int(posY+0.5), 1);
  display.drawPixel(int(posX+0.5), int(posY+0.5), 1);
  
  display.display();

  delay(5);
  
}
