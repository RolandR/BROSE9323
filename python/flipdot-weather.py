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
import requests
#from pyorbital.moon_phase import moon_phase

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

phase = 0.0
moonSize = 16;

bufferWidth = int((width+7)/8)
bufferSize = bufferWidth*height

displayData = bytearray(bufferSize)


outputImage = Image.new("1", (width, height), 0)
blankImage = outputImage.copy();
charset =  Image.open("./charset-bold.png").convert("RGB")
moonsImage =  Image.open("./moons.png").convert("RGB").getchannel("G")

def drawMoon(phase):
	phase = math.floor(phase*16)
	imgPos = phase*(moonSize+1)
	moon = moonsImage.copy().crop((imgPos, 0, imgPos+moonSize, moonSize))
	outputImage.paste(moon, (width-moonSize, 0))
	
def horizontalLine(xPos):
	for yPos in range(0, height):
		outputImage.putpixel((xPos, yPos), 1)

def writeText(text, pos):
	
	cursor = pos
	for char in text:
		charcode = ord(char)
		posX = (charcode%16)*charsetCellWidth
		posY = (math.floor(charcode/16)-2)*charsetCellHeight + charsetCellHeight-textHeight-1
		charImage = charset.copy().crop((posX, posY, posX+charsetCellWidth, posY+textHeight))
		charWidth = 0
		for x in range(charsetCellWidth):
			if charImage.getpixel((x, textHeight-1)) == (255, 0, 0):
				charWidth = x
				break
		outputImage.paste(charImage.getchannel("G").crop((0, 0, charWidth, textHeight)), tuple(cursor))
		cursor[0] += charWidth+1

def checkAPI():
	
	try:
		url = 'http://api.weatherapi.com/v1/forecast.json'

		params = dict(
			key="dd076aa3bacf4a56b6a145539230109",
			q="46.9,7.4",
		)

		resp = requests.get(url=url, params=params, timeout=5)
		resp.raise_for_status()
		data = resp.json()
		
		sunrise = data["forecast"]["forecastday"][0]["astro"]["sunrise"]
		sunrise = datetime.datetime.strptime(sunrise, "%I:%M %p")
		sunrise = sunrise.strftime("%H:%M")
		sunset = data["forecast"]["forecastday"][0]["astro"]["sunset"]
		sunset = datetime.datetime.strptime(sunset, "%I:%M %p")
		sunset = sunset.strftime("%H:%M")
		
		temp = data["current"]["temp_c"]
		if temp <= -10.0:
			temp = round(temp)
		maxTemp = data["forecast"]["forecastday"][0]["day"]["maxtemp_c"]
		if maxTemp <= -10.0:
			maxTemp = round(maxTemp)
		
		writeText("Á"+sunrise, [1, 0])
		writeText("Â"+sunset, [1, 9])		

		writeText(str(temp)+"°", [38, 0])
		writeText(str(maxTemp)+"°", [38, 9])
		
	# except requests.exceptions.HTTPError as err:
		# writeText("ui, Fähler:", [7, 0])
		# writeText(str(resp.status_code), [1, 9])
		# print(datetime.datetime.now())
		# print(err)
		# print("-----------------------------")
	# except requests.exceptions.ReadTimeout as err:
		# writeText("Dä Guru lat", [15, 0])
		# writeText("sech fei Zyt...", [7, 9])
		# print(datetime.datetime.now())
		# print(err)
		# print("-----------------------------")
	# except requests.exceptions.ConnectionError as err:
		# writeText("I verwütsche", [7, 0])
		# writeText("der Guru nid :(", [4, 9])
		# print(datetime.datetime.now())
		# print(err)
		# print("-----------------------------")
	# except requests.exceptions.RequestException as err:
		# writeText("Z Fax a Guru", [9, 0])
		# writeText("isch abverheit", [6, 9])
		# print(datetime.datetime.now())
		# print(err)
		# print("-----------------------------")
	except Exception as err:
		writeText("Ke Ahnig wieso,", [2, 0])
		writeText("aber es geit nid", [2, 9])
		print(datetime.datetime.now())
		print(err)
		print("-----------------------------")


def displayImage():
	
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


while True:
	checkAPI()
	horizontalLine(35)
	horizontalLine(65)
	#displayImage()
	#time.sleep(1)
	#displayImage()
	
	phase = 1/16;
	drawMoon(phase)
	displayImage()
	outputImage = blankImage.copy()
	time.sleep(5*60)