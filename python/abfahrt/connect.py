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
import re

def connectFlipdots():
	
	# autodetect arduino
	arduinos = []
	for p in serial.tools.list_ports.comports():
		if p.manufacturer and 'Arduino' in p.manufacturer:
			arduinos.append(p.device)

	#if not arduinos:
	#    raise IOError("No Arduino found")
	#if len(arduinos) > 1:
	#    warnings.warn('Multiple Arduinos found - using the first')

	serialConnections = []

	for a, arduino in enumerate(arduinos):
		# Mystery github code!
		# https://stackoverflow.com/a/45475068
		# This sets up a serial connection without resetting the arduino.
		port = arduino
		f = open(port)
		attrs = termios.tcgetattr(f)
		attrs[2] = attrs[2] & ~termios.HUPCL
		termios.tcsetattr(f, termios.TCSAFLUSH, attrs)
		f.close()
		connection = serial.Serial()
		connection.baudrate = 9600
		connection.port = port
		connection.writeTimeout = 0.2
		serialConnections.append(connection)


	maxAttempts = 10

	flipdots = {}

	for port in serialConnections:
		
		for i in range(maxAttempts):
			try:
				port.open()
				flipdotIdent = port.readline().decode()
				identMatch = re.search(r"Flipdot \d", flipdotIdent)
				
				if identMatch is not None:
					matchString = identMatch.group()
					flipdots[matchString] = port
					port.close()
					print("Detected {}".format(matchString))
					break
					
				port.close()
				
			except Exception as error:
				print("nope: ", error)
			
			if i == maxAttempts-1:
				print("Could not detect a flipdot on one of the ports:")
				print(port)
	
	return flipdots
