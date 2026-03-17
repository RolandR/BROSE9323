#!/usr/bin/python3

import os
import sys
import math
import time
from datetime import datetime, timedelta
import warnings
import serial
from PIL import Image
import json

from setText import *
from connect import *
import fahrplan

sys.path.insert(1, './fallblatt')

from showTalk import showTalk as fallblattShowTalk

params = {
	"flipdotsCount": 3,
	"height": 16,
	"width": 84,
	"smallestWhitespace": 3,
	"largestWhitespace":8,
}

flipdots = connectFlipdots()

replacements = {}

def displayImage(image, serialConnection):
	
	height = params["height"]
	width = params["width"]

	bufferWidth = int((width+7)/8)
	bufferSize = bufferWidth*height

	displayData = bytearray(bufferSize)
	
	for y in range(height):
		for xByte in range(bufferWidth):
			byteValue = 0;
			for bit in range(8):
				if(xByte*8+bit < width):
					if image.getpixel((xByte*8+bit, y)) != 0:
						byteValue += 2**(bit)
			displayData[y*bufferWidth+(xByte)] = byteValue;

	try:
		serialConnection.open()
		serialConnection.write(displayData)
		serialConnection.close()
	except Exception as error:
		print("nope: ", error)
		
def clear(serialConnection):
	
	height = params["height"]
	width = params["width"]

	bufferWidth = int((width+7)/8)
	bufferSize = bufferWidth*height
	
	displayData = bytearray(bufferSize)
	
	for y in range(height):
		for xByte in range(bufferWidth):
			displayData[y*bufferWidth+(xByte)] = 0;

	try:
		serialConnection.open()
		serialConnection.write(displayData)
		serialConnection.close()
	except Exception as error:
		print("nope: ", error)


def fill(serialConnection):
	
	height = params["height"]
	width = params["width"]

	bufferWidth = int((width+7)/8)
	bufferSize = bufferWidth*height
	
	displayData = bytearray(bufferSize)
	
	for y in range(height):
		for xByte in range(bufferWidth):
			displayData[y*bufferWidth+(xByte)] = 255;

	try:
		serialConnection.open()
		serialConnection.write(displayData)
		serialConnection.close()
	except Exception as error:
		print("nope: ", error)
		

def showTalk(talk, endTime):

	sleepytime = 0.3
	
	flipdotImages = setText(title, params)
	
	#return 0
	
	fallblattShowTalk(talk)

	displayImage(flipdotImages[0], flipdots["Flipdot 0"])
	time.sleep(sleepytime)

	displayImage(flipdotImages[1], flipdots["Flipdot 1"])
	time.sleep(sleepytime)

	displayImage(flipdotImages[2], flipdots["Flipdot 2"])
	time.sleep(sleepytime)
	
	keepAlive(endTime, flipdotImages, flipdots)
	
	#fill(flipdots["Flipdot 0"])
	#time.sleep(sleepytime)
	#fill(flipdots["Flipdot 1"])
	#time.sleep(sleepytime)
	#fill(flipdots["Flipdot 2"])
	#time.sleep(sleepytime)
	#clear(flipdots["Flipdot 0"])
	#time.sleep(sleepytime)
	#clear(flipdots["Flipdot 1"])
	#time.sleep(sleepytime)
	#clear(flipdots["Flipdot 2"])
	#time.sleep(sleepytime)
	
def keepAlive(endTime, flipdotImages, flipdots):
	
	fastSleepyTime = 0.2
	delayTime = 0.8
	
	while True:
		
		displayImage(flipdotImages[0], flipdots["Flipdot 0"])
		time.sleep(fastSleepyTime)

		displayImage(flipdotImages[1], flipdots["Flipdot 1"])
		time.sleep(fastSleepyTime)

		displayImage(flipdotImages[2], flipdots["Flipdot 2"])
		
		now = datetime.now().astimezone()
		if now >= endTime:
			return 0
		
		time.sleep(delayTime)

def fahrplanLoop():
	
	switchTime = 7
	
	while True:
		nextTalks = fahrplan.getTalks()
		
		for i in range(4):
			
			endTime = datetime.now().astimezone() + timedelta(seconds=switchTime)
			showTalk(nextTalks[i], endTime)


replacementsFile = open("replacements.json")
replacements = json.loads(replacementsFile.read())

fahrplanLoop()