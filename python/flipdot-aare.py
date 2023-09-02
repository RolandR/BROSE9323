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

bufferWidth = int((width+7)/8)
bufferSize = bufferWidth*height

displayData = bytearray(bufferSize)


outputImage = Image.new("1", (width, height), 0)
blankImage = outputImage.copy();
charset =  Image.open("./charset-bold.png").convert("RGB")

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

def checkGuru():
	
	try:
		gurUrl = 'https://aareguru.existenz.ch/v2018/current'

		params = dict(
			city="bern",
			app="flipdot.draemm.li",
			version="1.0.0"
		)

		resp = requests.get(url=gurUrl, params=params, timeout=5)
		resp.raise_for_status()
		data = resp.json()
		
		aareTemp = data["aare"]["temperature"]
		luftTemp = data["weather"]["current"]["tt"]
		flow = data["aare"]["flow"];
		
		
		if aareTemp is None:
			aareTemp = "??°"
		else:
			if aareTemp < -10.0:
				aareTemp = round(aareTemp)
			aareTemp = round(aareTemp, 1)
			aareTemp = "Ñ¡"+str(aareTemp)+"°"
			
		if luftTemp is None:
			luftTemp = "??°"
		else:
			if luftTemp < -10.0:
				luftTemp = round(luftTemp)
			luftTemp = round(luftTemp, 1)
			if luftTemp > 0:
				luftTemp = "Ò¡"+str(luftTemp)+"°"
			else:
				luftTemp = " Ó¡"+str(luftTemp)+"°"
		
		textli = "";
		
		if flow is None:
			flow = "??m³,"
			textli = " ke Ahnig"
		else:
			if   flow < 60:
				textli = " troche..."
			elif flow < 100:
				textli = " fasch nüt"
			elif flow < 150:
				textli = " nid¡so¡viu"
			elif flow < 200:
				textli = " grad¡guet"
			elif flow < 250:
				textli = " ender¡viu"
			elif flow < 300:
				textli = " mega viu"
			elif flow < 360:
				textli = "¡krass¡viu!"
			elif flow < 430:
				textli = " extrem!"
			elif flow < 500:
				textli = "  Fluet!"
			elif flow < 560:
				textli = "  Fluet!!!"
			else:
				textli = "   ! ! !"
			
			flow = str(flow)+"m³,"

		writeText(aareTemp, [1, 0])
		writeText(luftTemp, [43, 0])
		writeText(flow+textli, [1, 9])		
		
	except requests.exceptions.HTTPError as err:
		writeText("Em Guru geits", [7, 0])
		writeText("nid so guet: "+str(resp.status_code), [1, 9])
		print(datetime.datetime.now())
		print(err)
		print("-----------------------------")
	except requests.exceptions.ReadTimeout as err:
		writeText("Dä Guru lat", [15, 0])
		writeText("sech fei Zyt...", [7, 9])
		print(datetime.datetime.now())
		print(err)
		print("-----------------------------")
	except requests.exceptions.ConnectionError as err:
		writeText("I verwütsche", [7, 0])
		writeText("der Guru nid :(", [4, 9])
		print(datetime.datetime.now())
		print(err)
		print("-----------------------------")
	except requests.exceptions.RequestException as err:
		writeText("Z Fax a Guru", [9, 0])
		writeText("isch abverheit", [6, 9])
		print(datetime.datetime.now())
		print(err)
		print("-----------------------------")
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
	checkGuru()
	displayImage()
	time.sleep(1)
	displayImage()
	outputImage = blankImage.copy()
	time.sleep(5*60-1)