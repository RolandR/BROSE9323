#include <TimeLib.h>
#include <BROSE9323.h>


int height = 16;
int width = 84;
int panelWidth = 28;
int fliptime = 250;

int bufferWidth = (width+7)/8;
int bufferSize = bufferWidth*height;

struct Particle{
  signed char posX;
  signed char posY;
  bool frozen;
  bool active;
};

int currentlyActive = 0;
const int maxActive = 20;
const int particleCount = 200;
Particle particles[particleCount];

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

  for(int i = 0; i < particleCount; i++){
    particles[i].posX = int(random(0, 2)*width-1);
    particles[i].posY = random(0, height-1);
    particles[i].frozen = false;
    particles[i].active = false;
  }

  particles[0].posX = int(width/2);
  particles[0].posY = int(height/2);
  particles[0].frozen = true;
}

void loop() {
  
  display.fillScreen(0);

  for(int i = 0; i < particleCount; i++){

    if(!particles[i].frozen){

      if(currentlyActive < maxActive && !particles[i].active){
        particles[i].active = true;
        currentlyActive++;
      }
      
      for(int u = 0; u < particleCount; u++){
        if(particles[u].frozen){
          if(abs(particles[u].posX - particles[i].posX) <= 1 && abs(particles[u].posY - particles[i].posY) <= 1){
            particles[i].frozen = true;
            particles[i].active = false;
            currentlyActive -= 1;
            break;
          }
        }
      }
    }
    
    if(!particles[i].frozen && particles[i].active){
      
      particles[i].posX += random(0, 3)-1;
      particles[i].posY += random(0, 3)-1;
  
      if(particles[i].posX < 0){
        particles[i].posX = 0;
      } else if(particles[i].posX >= width){
        particles[i].posX = width-1;
      }
  
      if(particles[i].posY < 0){
        particles[i].posY = 0;
      } else if(particles[i].posY >= height){
        particles[i].posY = height-1;
      }
    }

    if(particles[i].frozen || particles[i].active){
      display.drawPixel(particles[i].posX, particles[i].posY, 1);
    }
  }

  display.display();

  delay(1);
  
}
