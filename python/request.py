#!/usr/bin/python3

import os
import sys
import math
import time
import termios
import warnings
from datetime import datetime, timezone, timedelta
import requests
import xml.etree.ElementTree as ET
from itertools import compress

def writeText(text, pos):
	print(text)
	
def printDepartures(departures):
	
	replacements = {
		"Bern Bahnhof": "Bern Bhf",
		"Köniz Weiermatt": "Köniz W.",
	}
	
	for departure in departures:
		
		line = departure["line"]
		destination = departure["destination"]
		direction = departure["direction"]
		time = departure["time"]
		minutesFromNow = departure["minutesFromNow"]
		
		
		if(destination in replacements):
			destination = replacements[destination]
		
		print("   {:>2s}".format(line) + " " + "{:8.8s}".format(destination) + " " + "{:3.0f}'".format(minutesFromNow))
			

def checkAPI():
	
	try:
		requestUrl = 'https://api.opentransportdata.swiss/ojp2020'

		headers = {
			"content-type":"application/xml",
			"authorization":"Bearer ",
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
		results = 10
		env = "_test"
		
		requestXML = requestXML.format(timestamp=now, numResults=results, env=env)
			
		ns = {"ojp":"http://www.vdv.de/ojp", "siri":"http://www.siri.org.uk/siri"}

		resp = requests.post(url=requestUrl, headers=headers, timeout=5, data=requestXML)
		resp.raise_for_status()
		
		resp.encoding = "utf-8"
		data = resp.text
		
		
		root = ET.fromstring(data)
		
		departures = []
		
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
		
		
		departures.sort(key=lambda x: x["minutesFromNow"])
		
		tramsEuropaplatz = filter(lambda x: (x["line"] == "7" or x["line"] == "8") and x["direction"] == "R" and x["minutesFromNow"] > 0.5, departures)
		tramsBern = filter(lambda x: (x["line"] == "7" or x["line"] == "8") and x["direction"] == "H" and x["minutesFromNow"] > 0.5, departures)
		busKoeniz = filter(lambda x: (x["line"] == "17") and x["direction"] == "R" and x["minutesFromNow"] > 0.5, departures)
		busBern = filter(lambda x: (x["line"] == "17") and x["direction"] == "H" and x["minutesFromNow"] > 0.5, departures)
		
		
		print()
		printDepartures(departures)
		print()
		print()
		print()
		printDepartures(compress(tramsBern, [1, 1]))
		print()
		printDepartures(compress(tramsEuropaplatz, [1, 1]))
		print()
		printDepartures(compress(busBern, [1]))
		printDepartures(compress(busKoeniz, [1]))
		print()
		
		
		
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

checkAPI()