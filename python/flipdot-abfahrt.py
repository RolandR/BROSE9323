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
from datetime import datetime, timezone, timedelta
import requests
import xml.etree.ElementTree as ET
from itertools import compress

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


#height = 16*3+16
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

apiKey = ""

with open('api-key', 'r') as file:
    apiKey = file.read().rstrip()

def printDepartures(departures, y, doDisplay):
	
	try:
		
		replacements = {
			"Bern Bahnhof": "Bern¡Bhf",
			"Bern, Bahnhof": "Bern¡Bhf",
			"Köniz Weiermatt": "Köniz¡W.",
			"Köniz, Weiermatt": "Köniz¡W.",
			"Bern, Saali": "Saali",
			"Bern, Ostring": "Ostring",
			"Bern, Bümpliz": "Bümpliz",
			"Bern Brünnen Westside, Bahnhof": "Brünnen",
			"Brünnen Bhf": "Brünnen",
			"Holenacker": "H'acker", # höhöhö, hacker
		}
		
		for departure in departures:
			
			line = departure["line"]
			destination = departure["destination"]
			direction = departure["direction"]
			time = departure["time"]
			minutesFromNow = departure["minutesFromNow"]
			
			displayTime = minutesFromNow
			if minutesFromNow > 60:
				displayTime = "{:2.0f}:{}".format(int(time.strftime("%H")), time.strftime("%M"))
			elif minutesFromNow < 2:
				displayTime = "¡¡Ô"
			else:
				displayTime = "{:1.0f}'".format(displayTime)
			
			
			if(destination in replacements):
				destination = replacements[destination]
			
			#print("   {:<2s}".format(line) + " " + "{:8.8s}".format(destination) + " " + "{:>5s}".format(displayTime) + " " + direction)
			print("   {:<2s}".format(line) + " " + "{:8s}".format(destination) + " " + "{:>5s}".format(displayTime) + " " + direction)
			
			if doDisplay:
				writeText("{:¡>2s}".format(line), [0, y])
				writeText("{:8.8s}".format(destination), [12, y])
				#writeText("{:3.0f}'".format(minutesFromNow), [59, y])
				writeText("{:¤>5s}".format(displayTime), [57, y])
				
	except Exception as err:
		outputImage = blankImage.copy()
		writeText("Es isch uf", [2, 0])
		writeText("d'Nase gheit", [2, 9])
		print(datetime.now())
		print(err)
		print("-----------------------------")
	
def horizontalLine(xPos):
	for yPos in range(0, height):
		outputImage.putpixel((xPos, yPos), 1)

def writeText(text, pos):
	
	pos[0] = pos[0]
	
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
		requestUrl = 'https://api.opentransportdata.swiss/ojp2020'

		headers = {
			"content-type":"application/xml",
			"authorization":"Bearer {}".format(apiKey),
		}
		
		requestXML = """<?xml version="1.0" encoding="UTF-8"?>
			<OJP xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns="http://www.siri.org.uk/siri" version="1.0" xmlns:ojp="http://www.vdv.de/ojp" xsi:schemaLocation="http://www.siri.org.uk/siri ../ojp-xsd-v1.0/OJP.xsd">
				<OJPRequest>
					<ServiceRequest>
						<RequestTimestamp>{timestamp}</RequestTimestamp>
						<RequestorRef>draemmli{env}</RequestorRef>
						<ojp:OJPStopEventRequest>
							<RequestTimestamp>{timestamp}</RequestTimestamp>
							<ojp:Location>
								<ojp:PlaceRef>
									<StopPlaceRef>8590041</StopPlaceRef>
									<ojp:LocationName>
										<ojp:Text>Bern, Loryplatz</ojp:Text>
									</ojp:LocationName>
								</ojp:PlaceRef>
								<ojp:DepArrTime>{timestamp}</ojp:DepArrTime>
							</ojp:Location>
							<ojp:Params>
								<ojp:NumberOfResults>{numResults}</ojp:NumberOfResults>
								<ojp:StopEventType>departure</ojp:StopEventType>
								<ojp:IncludeRealtimeData>true</ojp:IncludeRealtimeData>
							</ojp:Params>
						</ojp:OJPStopEventRequest>
					</ServiceRequest>
				</OJPRequest>
			</OJP>"""
		
		now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
		results = 15
		env = "_test"
		
		requestXML = requestXML.format(timestamp=now, numResults=results, env=env)
			
		ns = {"ojp":"http://www.vdv.de/ojp", "siri":"http://www.siri.org.uk/siri"}

		resp = requests.post(url=requestUrl, headers=headers, timeout=5, data=requestXML)
		resp.raise_for_status()
		
		resp.encoding = "utf-8"
		data = resp.text
		
		departures = []
		
		root = ET.fromstring(data)
		
		for stopEvent in root.findall(".//ojp:StopEvent", ns):
			
			timetabledTime = stopEvent.find(".//ojp:ThisCall", ns).find(".//ojp:TimetabledTime", ns)
			estimatedTime = stopEvent.find(".//ojp:ThisCall", ns).find(".//ojp:EstimatedTime", ns)
			
			if timetabledTime is not None:
				timetabledTime = timetabledTime.text
				ttTime = datetime.fromisoformat(timetabledTime).astimezone()
				ttTimeString = ttTime.strftime("%H:%M:%S")
			else:
				ttTimeString = ""
				
			if estimatedTime is not None:
				estimatedTime = estimatedTime.text
				estTime = datetime.fromisoformat(estimatedTime).astimezone()
				estTimeString = estTime.strftime("%H:%M:%S")
			else:
				if timetabledTime is not None:
					estimatedTime = timetabledTime
					estTime = ttTime
					estTimeString = ttTimeString
				else:
					estTimeString = ""
			
			timeFromNow = estTime - datetime.now().astimezone()
			minutesFromNow = timeFromNow.total_seconds()/60
				
			service = stopEvent.find(".//ojp:Service", ns)
			line = service.find(".//ojp:PublishedLineName", ns).find(".//ojp:Text", ns).text
			destination = service.find(".//ojp:DestinationText", ns).find(".//ojp:Text", ns).text
			direction = service.find(".//siri:DirectionRef", ns).text
			
			departure = {
				"line": line,
				"destination": destination,
				"direction": direction,
				"time": estTime,
				"minutesFromNow": minutesFromNow,
			}
			
			departures.append(departure)
			
		return departures
		
		
	except requests.exceptions.HTTPError as err:
		writeText("Em Guru geits", [7, 0])
		writeText("nid so guet: "+str(resp.status_code), [1, 9])
		print(datetime.now())
		print(err)
		print("-----------------------------")
	except requests.exceptions.ReadTimeout as err:
		writeText("Dä Guru lat", [15, 0])
		writeText("sech fei Zyt...", [7, 9])
		print(datetime.now())
		print(err)
		print("-----------------------------")
	except requests.exceptions.ConnectionError as err:
		writeText("I verwütsche", [7, 0])
		writeText("der Guru nid :(", [4, 9])
		print(datetime.now())
		print(err)
		print("-----------------------------")
	except requests.exceptions.RequestException as err:
		writeText("Z Fax a Guru", [9, 0])
		writeText("isch abverheit", [6, 9])
		print(datetime.now())
		print(err)
		print("-----------------------------")
	except Exception as err:
		writeText("Ke Ahnig wieso,", [2, 0])
		writeText("aber es geit nid", [2, 9])
		print(datetime.now())
		print(err)
		print("-----------------------------")


def processDepartures(departures):
	
	try:
		for dep in departures:
			timeFromNow = dep["time"] - datetime.now().astimezone()
			minutesFromNow = timeFromNow.total_seconds()/60
			dep["minutesFromNow"] = minutesFromNow
		
		printDepartures(departures, 0, False)
		
		departures.sort(key=lambda x: x["minutesFromNow"])
		
		departures = list(filter(lambda x: x["minutesFromNow"] > 1.5, departures))
		departures = list(filter(lambda x: x["destination"] != "Kaufm.Verband", departures))
		
		tramsEuropaplatz = list(filter(lambda x: (x["line"] == "7" or x["line"] == "8") and x["direction"] == "R", departures))
		tramsBern = list(filter(lambda x: (x["line"] == "7" or x["line"] == "8") and x["direction"] == "H", departures))
		busKoeniz = list(filter(lambda x: (x["line"] == "17") and x["direction"] == "R", departures))
		busBern = list(filter(lambda x: (x["line"] == "17") and x["direction"] == "H", departures))
		allBern = list(filter(lambda x: x["direction"] == "H", departures))
		
		print()
		print("All Bern:")
		printDepartures(allBern, 0, False)
		print("Tram Bern:")
		printDepartures(tramsBern, 0, False)
		print("Tram Europaplatz:")
		printDepartures(tramsEuropaplatz, 9, False)
		print("Bus Bern:")
		printDepartures(busBern, 0, False)
		print("Bus Köniz:")
		printDepartures(busKoeniz, 9, False)
		
		print()
		print()
		
		
		#printDepartures(compress(tramsBern, [1, 0]), 0, True)
		#printDepartures(compress(tramsEuropaplatz, [1, 0]), 9, True)
		
		printDepartures(allBern[0:1], 0, True)
		#printDepartures(allBern[1:2], 9, True)
		printDepartures(tramsEuropaplatz[0:1], 9, True)
		#printDepartures(busKoeniz[0:1], 16+8+9, True)
		
		# printDepartures(tramsBern[0:1], 0, True)
		# printDepartures(tramsBern[1:2], 9, True)
		# printDepartures(tramsEuropaplatz[0:1], 16+8, True)
		# printDepartures(tramsEuropaplatz[1:2], 16+8+9, True)
		# printDepartures(busBern[0:1], 32+16, True)
		# printDepartures(busKoeniz[0:1], 32+16+9, True)
		
		# printDepartures(departures[0:1], 0, True)
		# printDepartures(departures[1:2], 9, True)
		# printDepartures(departures[2:3], 16+8, True)
		# printDepartures(departures[3:4], 16+8+9, True)
		# printDepartures(departures[4:5], 32+16, True)
		# printDepartures(departures[5:6], 32+16+9, True)
		print()
		print("--------------------------------------------------------------------------------------")
		print()
		#printDepartures(compress(busBern, [1]))
		#printDepartures(compress(busKoeniz, [1]))
	except Exception as err:
		outputImage = blankImage.copy()
		writeText("Schinbar si aui", [4, 0])
		writeText("¡Tram kaputt :(", [4, 9])
		print(datetime.now())
		print(err)
		print("-----------------------------")

def displayImage():
	
	transformedImage = outputImage.rotate(180)
	for y in range(height):
		for xByte in range(bufferWidth):
			byteValue = 0;
			for bit in range(8):
				if(xByte*8+bit < width):
					if transformedImage.getpixel((xByte*8+bit, y)) != 0:
						byteValue += 2**(bit)
			displayData[y*bufferWidth+(xByte)] = byteValue;

	try:
		arduinoSerial.open()
		arduinoSerial.write(displayData)
		arduinoSerial.close()
	except Exception as error:
		print("nope: ", error)
		
	outputImage.save("outputImage.png")

timeOfLastRequest = datetime.now();
departures = checkAPI()

while True:
	now = datetime.now()
	secondsSinceLastRequest = (now - timeOfLastRequest).total_seconds()
	if secondsSinceLastRequest >= 20:
		departures = checkAPI()
		timeOfLastRequest = now
	processDepartures(departures)
	displayImage()
	outputImage = blankImage.copy()
	time.sleep(1)