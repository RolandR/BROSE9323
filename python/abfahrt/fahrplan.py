#!/usr/bin/python3

import os
import sys
import math
import requests
import json
from datetime import datetime, timezone, timedelta
from dateutil.parser import parse

fahrplan = None

def updateFahrplan():		
	
	requestUrl = "https://cfp.winterkongress.ch/wk26/schedule/export/schedule.json"
	
	resp = requests.get(url=requestUrl, timeout=5)
	
	resp.raise_for_status()
	resp.encoding = "utf-8"
	data = resp.text
	fahrplan = json.loads(data)
	
	days = fahrplan["schedule"]["conference"]["days"]
	
	talks = [];
	
	for day in days:
		
		rooms = [
			"Aktionshalle",
			"Clubraum",
			"Fabriktheater"
		];
		
		for roomName in rooms:
			
			room = day["rooms"][roomName]
			
			for talk in room:
				
				talks.append(talk)
	
	fahrplan = talks
	return talks
	
def isInThePast(talk):
	
	now = datetime.now().astimezone()
	talkTime = parse(talk["date"])
	
	return now < talkTime

def getTalks():
	
	if fahrplan is None:
		talks = updateFahrplan()
	else:
		talks = fahrplan
		
	talks = filter(isInThePast, talks)
	talks = sorted(talks, key=lambda talk: talk["date"])
	
	return talks
	
	#print(talks[0]["title"])
	#print(talks[1]["title"])
	#print(talks[2]["title"])
	
def periodicUpdate():
	
	updateFrequency = 5*60
	
	while True:
		updateFahrplan()
		time.sleep(updateFrequency)
		
	