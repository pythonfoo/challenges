__author__ = 'bison'

import time
import socket
import msgpack
import random
import pygame

import os

if os.path.isfile('conf_local.py'):
	print 'import conf local'
	import conf_local as conf
else:
	import conf


class client(object):
	def __init__(self):
		self.stillAlive = True
		self.printDebug = True
		self.printDoing = True

		self.s = socket.socket()
		self.s.settimeout(0.08)  # wait x seconds for receiving
		self.socketEmptyCounter = 0  # Socket disconnect fix!
		self.unpacker = msgpack.Unpacker()

		# bot Vars
		self.address = conf.SERVER_IP  # '172.22.27.191' '192.168.1.117'
		self.name = conf.PLAYER_NAME
		self.password = conf.PLAYER_PW
		self.port = conf.SERVER_PORT
		self.s.connect((self.address, self.port))

		# game vars
		self.playerDict = {}

		# pygame
		self.screen = None

	def debug(self, txt, override=True):
		if self.printDebug or override:
			print txt

	def dRecieve(self):
		if self.stillAlive == False:
			return False

		tmp = ''
		socketEmptyCounterIn = 0
		try:
			while socketEmptyCounterIn <= 5:
				tmp += self.s.recv(4096)
				if tmp == '':
					socketEmptyCounterIn += 1
					if socketEmptyCounterIn >= 4:
						self.debug('no rec.:' + str(self.socketEmptyCounter), True)
						#time.sleep(0.01)
		except socket.timeout:
			if tmp != '':
				pass
				#self.debug('|incomplete command: ' + tmp, True)
		except Exception, e:
			self.debug('Recieved UNKNOWN ERROR (LEAVING): ' + str(e), True)


		answer = None
		try:
			self.unpacker.feed(tmp)
			answer = self.unpacker.unpack()
		except Exception as ex:
			pass

		return answer

	def dSend(self, dictData):
		if self.stillAlive == False:
			return False

		self.s.send(msgpack.dumps(dictData))

	def drawEnemys(self, enemyArray=[]):
		#(((15, 48), 'd', '3', 'Theseus by hwm'), ((43, 0), 'a', '4', 'gglyptodon'), ((10, 48), 'a', '2', 'YtvwlD'), ((1, 0), 'd', '1', 'bison'))

		for enemy in enemyArray:
			x, y = enemy[0]
			name = enemy[3]

			if not name in self.playerDict:
				self.playerDict[name] = (0, random.randint(0,255), random.randint(0,255))

			pygame.draw.rect(self.screen, self.playerDict[name] , (x*conf.BLOCK_SIZE, y*conf.BLOCK_SIZE, conf.BLOCK_SIZE,  conf.BLOCK_SIZE))

	def drawBombs(self, bombArray=[]):
		#(((23, 28), 0.5502138137817383, 'burning'), ((42, 5), 3.5247445106506348, 'ticking'))
		for bomb in bombArray:
			x, y = bomb[0]
			bState = bomb[1]
			color = None
			if bState == 'burning':
				color = (255, 5, 5)
			else:
				color = (255, 255, 255)
			pygame.draw.rect(self.screen, conf.COLOR_BOMB, (x*conf.BLOCK_SIZE, y*conf.BLOCK_SIZE, conf.BLOCK_SIZE,  conf.BLOCK_SIZE))

	def drawMap(self, mapString=''):
		# g: Weg
		# M: unzerstoerbarer Block
		# W: zerstoerbarer Block
		# w: zerstoerter Block
		if mapString is None:
			return

		#print map.split("\n")

		wholeMap = mapString.split("\n")
		for y, line in enumerate(wholeMap):
			for x, cell in enumerate(line):

				relX = x * conf.BLOCK_SIZE
				relY = y * conf.BLOCK_SIZE
				#print y, relX, relY

				color = None
				if cell == 'g' or cell == 'w':
					color = conf.COLOR_WALKABLE
					#pass
				elif cell == 'W':
					color = conf.COLOR_DESTRUCTIBLE
				elif cell == 'M':
					color = conf.COLOR_INDESTRUCTIBLE
				else:
					print 'WAT:', cell

				if color:
					#print relX, relY
					pygame.draw.rect(self.screen, color, (relX, relY, conf.BLOCK_SIZE,  conf.BLOCK_SIZE))
					#print x, y
					#print relX, relY, relX + conf.BLOCK_SIZE, relY + conf.BLOCK_SIZE

		#print rowX,rowY

	def run(self):
		isRunning = True
		connectAs = { "type": "connect", "username": self.name, "password": self.password, "async": False}
		self.dSend(connectAs)
		print self.dRecieve()

		# Game parameters
		self.SCREEN_WIDTH = conf.SCREEN_WIDTH
		self.SCREEN_HEIGHT = conf.SCREEN_HEIGHT
		BG_COLOR = conf.COLOR_BG
		self.BLOCK_SIZE = conf.BLOCK_SIZE

		pygame.init()

		self.REST_WITH = self.SCREEN_WIDTH % self.BLOCK_SIZE
		self.REST_HEIGHT = self.SCREEN_HEIGHT % self.BLOCK_SIZE
		self.DRAW_RECT = pygame.Rect(0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
		# do fancy window stuff
		pygame.display.set_caption("pybeBomb")
		#pygame.display.set_icon(pygame.image.load('imgs/bandit.jpg'))
		pygame.mouse.set_visible(False)

		if not conf.FULL_SCREEN:
			#os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (conf.WINDOW_POSITION_X, conf.WINDOW_POSITION_Y)
			#if not conf.WINDOW_BORDER:
			#	self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.NOFRAME, 32)

			if self.screen is None:
				self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), 0, 32)

		clock = pygame.time.Clock()
		redrawCount = 0

		keymap = {pygame.K_UP: 'w', pygame.K_RIGHT: 'd', pygame.K_DOWN: 's', pygame.K_LEFT: 'a',
					pygame.K_b: 'b', pygame.K_QUESTION: '?',
					pygame.K_ESCAPE: 'q', pygame.K_q: 'q'
				}
		fuseTimer = 5

		while isRunning:
			time_passed = clock.tick(50)
			redrawCount += time_passed

			doActions = ''
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					isRunning = False
				elif event.type == pygame.KEYDOWN:
					if event.key in keymap:
						doActions += keymap[event.key]
					elif event.key >= pygame.K_0 and event.key <= pygame.K_9:
						fuseTimer = event.key -48  # normalize the key code back to seconds
						print 'fusetime:', fuseTimer
					else:
						print "event.key:", event.key
				else:
					pass

			redrawCount += 1
			if redrawCount >= 2:  #or len(doActions) == 0:
				# ONLY move, when the timer elapses!
				# otherwise you could change the direction multiple times before the scenery changes and upates
				# strange shit goes on!
				redrawCount = 0
				doActions += 'm*#'

			for cmd in doActions:
				rawSend = None
				if cmd == 'w' or cmd == 'a' or cmd == 's' or cmd == 'd':
					rawSend = { "type": "move", "direction": cmd, "distance": 1 }

				if cmd == '?':
					rawSend = { "type": "whoami" }

				if cmd == 'b':
					rawSend = { "type": "bomb", "fuse_time": fuseTimer }

				if cmd == 'm':
					rawSend = { "type": "map" }

				if cmd == '#':
					rawSend = { "type": "what_bombs" }

				if cmd == '*':
					rawSend = { "type": "what_foes" }

				if cmd == 'q':
					isRunning = False


				if rawSend:
					self.dSend(rawSend)

				recieved = self.dRecieve()
				if isinstance(recieved, int):
					print 'ERROR recieved:', recieved
				elif recieved and len(recieved) > 0:
					recCommand = recieved[0]
					#print recCommand
					if recCommand == 'MAP':
						#print recieved[1]
						#pygame.draw.rect(self.screen, BG_COLOR, self.DRAW_RECT)
						self.screen.fill(BG_COLOR)
						self.drawMap(recieved[1])
					elif recCommand == 'WHAT_BOMBS':
						print self.drawBombs(recieved[1])
					elif recCommand == 'WHAT_FOES':
						self.drawEnemys(recieved[1])
					elif recCommand == '?':
						#self.client.inform("OK", [self.color, self.id, self._top, self._left])
						print 'state', 'color', 'id', 'top', 'left'
						print recieved[0], recieved[1][0], recieved[1][1], recieved[1][2], recieved[1][3]

			pygame.display.flip()

		self.s.close()


if __name__ == '__main__':
	cls = client()
	cls.run()