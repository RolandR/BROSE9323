#!/usr/bin/python3

import os
import sys
import math
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

textHeight = 7
charsetCellHeight = 10
charsetCellWidth = 10

text = "Andi het e Job :)"

bufferWidth = int((width+7)/8)
bufferSize = bufferWidth*height

displayData = bytearray(bufferSize)


outputImage = Image.new("1", (width, height), 0)
charset =  Image.open("./charset-bold.png").convert("RGB")

def writeText(text, pos):
	
	cursor = pos
	for char in text:
		charcode = ord(char)
		posX = (charcode%16)*charsetCellWidth
		posY = (math.floor(charcode/16)-2)*charsetCellHeight + charsetCellHeight-textHeight-1
		charImage = charset.copy().crop((posX, posY, posX+charsetCellWidth, posY+textHeight))
		charWidth = 0
		for x in range(charsetCellWidth-1):
			if charImage.getpixel((x, textHeight-1)) == (255, 0, 0):
				charWidth = x
				break
		outputImage.paste(charImage.getchannel("G").crop((0, 0, charWidth, textHeight)), tuple(cursor))
		cursor[0] += charWidth+1

#writeText("Hello, World!", [0, 0]);
#writeText("Blorg blorg", [0, 8]);

if len(sys.argv) >= 2:
	writeText(sys.argv[1], [0, 0]);

if len(sys.argv) >= 3:
	writeText(sys.argv[2], [0, 8]);


for y in range(height):
	for xByte in range(bufferWidth):
		byteValue = 0;
		for bit in range(8):
			if(xByte*8+bit < width):
				if outputImage.getpixel((xByte*8+bit, y)) != 0:
					byteValue += 2**(bit)
		displayData[y*bufferWidth+xByte] = byteValue;

try:
	arduinoSerial.open()
	arduinoSerial.write(displayData)
	arduinoSerial.close()
except Exception as error:
	print("nope: ", error)