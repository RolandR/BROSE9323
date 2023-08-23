#!/usr/bin/python3

import os
import sys
import serial
import serial.tools.list_ports
import time
from PIL import Image
import termios
import warnings
import datetime

# autodetect arduino
arduinos = []
for p in serial.tools.list_ports.comports():
    if p.manufacturer and 'Arduino' in p.manufacturer:
        arduinos.append(p.device)

if not arduinos:
    raise IOError("No Arduino found")
if len(arduinos) > 1:
    warnings.warn('Multiple Arduinos found - using the first')

# Mystery github code!
# https://stackoverflow.com/a/45475068
# This sets up a serial connection without resetting the arduino.
port = arduinos[0]
f = open(port)
attrs = termios.tcgetattr(f)
attrs[2] = attrs[2] & ~termios.HUPCL
termios.tcsetattr(f, termios.TCSAFLUSH, attrs)
f.close()
arduinoSerial = serial.Serial()
arduinoSerial.baudrate = 9600
arduinoSerial.port = port
arduinoSerial.writeTimeout = 0.2


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

previousTime = [0, 0, 0, 0, 0, 0]

while True:
	now = datetime.datetime.now()
	currentTime = [int(now.hour/10), now.hour%10, int(now.minute/10), now.minute%10, int(now.second/10), now.second%10]
	
	if(currentTime != previousTime):

		previousTime = currentTime

		charHeight = 11
		yOffset = 3

		for i, char in enumerate(currentTime):
			if i%2 == 1:
				xOffset = 1
			else:
				xOffset = 0
				
			for y in range(charHeight):
				
				if (y == 4 or y == 6) and (i == 1 or i == 3):
					dot = 2**7
				else:
					dot = 0
				
				byteValue = 0
				for bit in range(8):
					if pix[char*8+bit+xOffset, y][0] > 128:
						byteValue += 2**(bit)
				byteValue += dot
				displayData[(y+yOffset)*bufferWidth+i+2] = byteValue
				
		try:
			arduinoSerial.open()
			arduinoSerial.write(displayData)
			arduinoSerial.close()
		except Exception as error:
			print("nope: ", error)
			print(currentTime)
			print("----------------")
		
	time.sleep(0.005)