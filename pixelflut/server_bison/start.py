#! /usr/bin/env python
import os, sys
from random import randint, choice
from math import sin, cos, radians

import pygame
import json
from pygame.sprite import Sprite


class screener(object):
	def __init__(self):
		self.screen = None
		self.mouseLastLeftDown = False
		self.countWin = 0
		self.countLose = 0
		self.countRound = 0

	def recieveValue(self, s):
		jsonRes  = None
		hasEx = False
		try:

			conn, addr = s.accept()
			#print 'Connected by', addr
			try:
				while 1:
					data = conn.recv(2048)
					#print 'data"', data, '"'
					hasEx = False
					if not data:
						break
					try:
						jsonRes = json.loads(data)
					except Exception as ex:
						print 'json error', ex
						conn.sendall('json error')
						hasEx = True

					if hasEx == False:
						if not 'user' in jsonRes:
							hasEx = True
							conn.sendall('NO USER!')
						elif not 'x' in jsonRes or not 'y' in jsonRes or not isinstance(jsonRes['x'], int) or not isinstance(jsonRes['y'], int):
							hasEx = True
							conn.sendall('NO X OR Y!')
						elif  not 'color' in jsonRes:
							hasEx = True
							conn.sendall('color error')
						elif not isinstance(jsonRes['color'], tuple) and not isinstance(jsonRes['color'], dict) and not isinstance(jsonRes['color'], list) :
							hasEx = True
							conn.sendall('color list error')
						elif len(jsonRes['color']) != 3 or jsonRes['color'][0] > 255 or jsonRes['color'][1] > 255 or jsonRes['color'][2] > 255\
								or jsonRes['color'][0] < 0 or jsonRes['color'][1] < 0 or jsonRes['color'][2] < 0:
							hasEx = True
							conn.sendall('color out of range error')
						elif jsonRes['x'] > self.SCREEN_WIDTH or jsonRes['y'] > self.SCREEN_HEIGHT:
							hasEx = True
							conn.sendall('out of bounds')
						#{"x": "pixelWut.py", "color": [15, 45, 63], "y": "2", "test": "bla", "user": "Plant"}
					else:
						conn.sendall('ok')

					conn.sendall('ok')
			finally:
				if conn != None:
					try:
						conn.close()
					except Exception as ex:
						hasEx = True
						print ex
		except Exception as ex:
			hasEx = True
			print ex
		#return {"user":"hwm","x":450,"y":322,"color":[255,255,0]}
		if hasEx:
			return None
		else:
			return jsonRes

	def run_game(self):
		# Game parameters
		self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 1024, 600
		BG_COLOR = 0, 0, 0

		pygame.init()

		# do fancy window stuff
		pygame.display.set_caption("PIXELFLUT CHALLENGE")

		self.screen = pygame.display.set_mode(
					(self.SCREEN_WIDTH, self.SCREEN_HEIGHT), 0, 32)
		clock = pygame.time.Clock()


		# some vars only for the game loop
		mouseX = 0
		mouseY = 0
		LEFT = 1
		spinWheels = False
		redrawCount = 0


		import socket
		import sys
		import json
		HOST = None			   # Symbolic name meaning all available interfaces
		PORT = 9999			  # Arbitrary non-privileged port
		s = None
		for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
									  socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
			af, socktype, proto, canonname, sa = res
			try:
				s = socket.socket(af, socktype, proto)
			except socket.error as msg:
				s = None
				continue
			try:
				s.bind(sa)
				s.listen(1)
			except socket.error as msg:
				s.close()
				s = None
				continue
			break
		srface = pygame.Surface([self.SCREEN_WIDTH, self.SCREEN_HEIGHT], pygame.SRCALPHA, 32)
		allPixel = {}
		# The main game loop
		#
		while True:
			# Limit frame speed to 50 FPS
			#
			time_passed = clock.tick(50)
			redrawCount += time_passed

			roundEnded = False
			mouseKlickedLeft = False
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.exit_game()
				elif event.type == pygame.MOUSEMOTION:
					mouseX, mouseY = event.pos

			if mouseKlickedLeft:
				print "klicked at:", mouseX, mouseY

			# limit the refreshrate further!
			if redrawCount >= 59 or mouseKlickedLeft:
				# Redraw the background
				self.screen.fill(BG_COLOR)

				vals = self.recieveValue(s)
				if vals != None:
					xy = (vals['x'], vals['y'])
					allPixel[xy] = vals

				userCounter = {}
				for val in allPixel.values():
					srface.set_at((val['x'],val['y']), val['color'])
					#self.incrementDict(vals['user'] ,userCounter)
					#if not vals['user'] in userCounter:
					#	userCounter[vals['user'] ] = 0
					#userCounter[vals['user']] += 1
					userCounter[val['user']] = userCounter.get(val['user'], 0) +1

				print 10 * '*'
				print userCounter

				self.screen.blit(srface, (0,0))

				pygame.display.flip()

	def incrementDict(self, key, dictvm):
		if not key in dictvm:
			dictvm[key] = 0

		dictvm[key] += 1

	def exit_game(self):
		sys.exit()

bnd = screener()
bnd.run_game()