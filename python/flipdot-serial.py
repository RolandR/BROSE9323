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

try:
	arduinoSerial.open()
	arduinoSerial.write(displayData)
	arduinoSerial.close()
except Exception as error:
	print("nope: ", error)