#!/usr/bin/python3

import os
import sys
import math
import time
from PIL import Image
import warnings

def setText(text, params):
	
	flipdotsSpacing = 5
	
	def buildCharset(charsetStartingCodepoints):
		
		charsetGridSize = 10
		charHeight = 7
		charsetRowCount = 16
		charsetColumnCount = 16
		
		charset = {}
		
		for startingCodepoint in charsetStartingCodepoints:
			
			charsetImage = Image.open("../charset-bold-{}.png".format(startingCodepoint)).convert("RGB")
			
			codepoint = startingCodepoint
			
			for y in range(charsetRowCount):
				for x in range(charsetColumnCount):
					symbol = chr(codepoint)
					
					posX = x*charsetGridSize
					posY = y*charsetGridSize+(charsetGridSize-charHeight-1)
					charImage = charsetImage.copy().crop((posX, posY, posX+charsetGridSize, posY+charHeight))
					
					charWidth = 0
					for x in range(charsetGridSize):
						if charImage.getpixel((x, charHeight-1)) == (255, 0, 0):
							charWidth = x
							break
					
					if charWidth == 0:
						codepoint += 1
						continue
					
					charImage = charImage.getchannel("G").crop((0, 0, charWidth, charHeight))
					
					charset[symbol] = charImage
					codepoint += 1
					
		return charset
	
	def flowText(text, charset):
		
		textInfo = []
		text = text.split(" ")
		
		for word in text:
			wordWidth = 0
			
			for i in range(len(word)):
				if not charset[word[i]]:
					print("Missing glyph: {}".format(word[i]))
					word[i] = "?"
				wordWidth += charset[word[i]].width + 1
			
			if wordWidth > 0:
				textInfo.append({
					"text": word,
					"width": wordWidth-1,
				})
		
		lines = [
			{
				"words": [],
				"width": 0,
			},
		]
		currentLine = 0
		
		for word in textInfo:
			
			if word["width"] > params["width"]:
				print("Word is wider than flipdot: "+word["text"])
			
			if lines[currentLine]["width"] == 0:
				lines[currentLine]["words"].append(word)
				lines[currentLine]["width"] += word["width"]
				
			elif lines[currentLine]["width"] + (word["width"] + params["smallestWhitespace"]) <= params["width"]:
				lines[currentLine]["words"].append(word)
				lines[currentLine]["width"] += word["width"] + params["smallestWhitespace"]
				
			else:
				
				currentLine += 1
				lines.append({
					"words": [],
					"width": 0,
				})
				
				lines[currentLine]["words"].append(word)
				lines[currentLine]["width"] += word["width"]
				
		
		for line in lines:
			line["text"] = ""
			lineWords = []
			for word in line["words"]:
				lineWords.append(word["text"])
			line["text"] = " ".join(lineWords)
		return lines
	
	def drawText(text, x, y, image, charset):
		
		for i in range(len(text)):
			char = text[i]
			if not charset[char]:
				print("Missing glyph: {}".format(char))
				continue
				
			image.paste(charset[char], (x, y))
			x += charset[char].width + 1
			
	def drawLine(line, x, y, image, charset, space):
		
		for word in line["words"]:
			drawText(word["text"], x, y, image, charset)
			x += word["width"] + space
	
	def drawLines(lines, flipdotImages, charset):
		for i, line in enumerate(lines):
			
			if len(lines) > 3:
				flipdot = math.floor(i/2)
				yPos = 9*(i % 2)
			else:
				flipdot = i
				yPos = 5
			
			additionalSpace = 0
		
			if(len(line["words"]) > 1):
				additionalSpace = math.floor((params["width"] - line["width"])/(len(line["words"])-1))
				additionalSpace = min(additionalSpace, params["largestWhitespace"]-params["smallestWhitespace"])
				
			totalAdditionalSpace = additionalSpace * (len(line["words"])-1)
			
			startX = math.floor(params["width"]/2 - (line["width"]+totalAdditionalSpace)/2)
			
			if(flipdot < len(flipdotImages)):
				drawLine(
					line,
					startX,
					yPos,
					flipdotImages[flipdot],
					charset,
					params["smallestWhitespace"] + additionalSpace,
				)
			else:
				print("Line won't fit:")
				print('"{}"'.format(line["text"]))
		
	
	def combineFlipdots(flipdotImages, flipdotsImage):
		for i, image in enumerate(flipdotImages):
			flipdotsImage.paste(image, (flipdotsSpacing, i*(params["height"]+flipdotsSpacing)+flipdotsSpacing))
	
	flipdotImage = Image.new("1", (params["width"], params["height"]), 0)
	
	flipdotImages = [
		flipdotImage.copy(),
		flipdotImage.copy(),
		flipdotImage.copy(),
	]
	
	flipdotsImage = Image.new(
		"RGB",
		(params["width"]+2*flipdotsSpacing, (params["height"]+flipdotsSpacing)*params["flipdotsCount"]+flipdotsSpacing),
		0x444444
	)
	
	charsetStartingCodepoints = [0, 8192]
	charset = buildCharset(charsetStartingCodepoints)
	
	lines = flowText(text, charset)
	
	drawLines(lines, flipdotImages, charset)
	
	combineFlipdots(flipdotImages, flipdotsImage)
	
	flipdotsImage.save("outputImage.png")
	
	return flipdotImages
	