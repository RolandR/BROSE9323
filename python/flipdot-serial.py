#!/usr/bin/python3

import os
import sys
import serial
import time
from PIL import Image
import termios


# Mystery github code!
# https://stackoverflow.com/a/45475068
port = '/dev/ttyACM0'
f = open(port)
attrs = termios.tcgetattr(f)
attrs[2] = attrs[2] & ~termios.HUPCL
termios.tcsetattr(f, termios.TCSAFLUSH, attrs)
f.close()
arduino = serial.Serial()
arduino.baudrate = 9600
arduino.port = port
print('dtr =', arduino.dtr)
arduino.open()


height = 16
width = 84
panelWidth = 28
fliptime = 280

bufferWidth = int((width+7)/8)
bufferSize = bufferWidth*height

displayData = bytearray(bufferSize)


imagePath = sys.argv[1]
#if os.path.exists(path):

im = Image.open(imagePath)
pix = im.load()

for y in range(height):
	for xByte in range(bufferWidth):
		byteValue = 0;
		for bit in range(8):
			if(xByte*8+bit < width):
				if pix[xByte*8+bit, y][0] > 128:
					byteValue += 2**(bit)
		displayData[y*bufferWidth+xByte] = byteValue;
		
arduino.write(displayData)