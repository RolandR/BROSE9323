#!/usr/bin/python3

import os
import sys
import serial
import time
from PIL import Image
import termios
import datetime


# Mystery github code!
# https://stackoverflow.com/a/45475068
port = '/dev/ttyUSB0'
f = open(port)
attrs = termios.tcgetattr(f)
attrs[2] = attrs[2] & ~termios.HUPCL
termios.tcsetattr(f, termios.TCSAFLUSH, attrs)
f.close()
arduino = serial.Serial()
arduino.baudrate = 9600
arduino.port = port
arduino.open()


height = 16
width = 84
panelWidth = 28
fliptime = 280

bufferWidth = int((width+7)/8)
bufferSize = bufferWidth*height

displayData = bytearray(bufferSize)


charsetPath = 'charset.png'
im = Image.open(charsetPath)
pix = im.load()

while True:
	now = datetime.datetime.now()
	currentTime = [int(now.hour/10), now.hour%10, int(now.minute/10), now.minute%10, int(now.second/10), now.second%10];

	charHeight = 11;
	yOffset = 3;

	for i, char in enumerate(currentTime):
		if i%2 == 1:
			xOffset = 1;
		else:
			xOffset = 0;
			
		for y in range(charHeight):
			
			if (y == 4 or y == 6) and (i == 1 or i == 3):
				dot = 2**7;
			else:
				dot = 0;
			
			byteValue = 0;
			for bit in range(8):
				if pix[char*8+bit+xOffset, y][0] > 128:
					byteValue += 2**(bit)
			byteValue += dot;
			displayData[(y+yOffset)*bufferWidth+i+2] = byteValue;
			
	arduino.write(displayData)
	
	time.sleep(1);