__author__ = 'bison'

import time
import socket
import msgpack
import random
import pygame
import conf
#msgpack-python

class client(object):
	def __init__(self):
		self.stillAlive = True
		self.printDebug = True
		self.printDoing = True

		self.s = socket.socket()
		self.s.settimeout(0.1) # wait x seconds for recieving
		self.socketEmptyCounter = 0 # Scoket disconnect fix!

		# bot Vars
		self.address = '172.22.27.191'
		self.port = 8001
		self.s.connect((self.address, self.port))

		#
		#self.level =
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
						time.sleep(0.05)

		except socket.timeout:
			if tmp != '':
				pass
				#self.debug('|incomplete command: ' + tmp, True)

		except Exception, e:
			self.debug('Recieved UNKNOWN ERROR (LEAVING): ' + str(e), True)

		# exceptions for discontinuing
		#if self.socketEmptyCounter >= 42:
		#	raise RuntimeError('connection loss')

		if tmp:
			return msgpack.loads(tmp)
		else:
			return None

	def dSend(self, dictData):
		if self.stillAlive == False:
			return False

		self.s.send(msgpack.dumps(dictData))

	def aiRand(self):
		actions = ['w', 'a', 's', 'd', 'b']
		return random.choice(actions)

	def aiRand2(self):
		actions = ['a', 'w', 'b']
		return random.choice(actions)

	def drawMap(self, map=''):
		# g: Weg
		# M: unzerstoerbarer Block
		# W: zerstoerbarer Block
		# w: zerstoerter Block

		#print map.split("\n")
		rowX = 0
		rowY = 0
		for x in map.split("\n"):
			rowY = 0
			for y in x:

				relX = rowX * conf.BLOCKSIZE
				relY = rowY * conf.BLOCKSIZE
				#print y, relX, relY

				color = None
				if y == 'g' or y == 'w':
					color = conf.COLOR_WALKABLE
				elif y == 'W':
					color = conf.COLOR_DEST
				elif y == 'M':
					color = conf.COLOR_INDESTRUCTABLE
				else:
					print 'WAT:', y

				if color:
					#print relX, relY
					pygame.draw.rect(self.screen, color, (relX, relY, relX + conf.BLOCKSIZE, relY + conf.BLOCKSIZE))
				rowY += 1
			rowX += 1
	def run(self):
		isRunning = True
		name = "bot"+str(random.randint(0,1000))
		name = 'bison'
		print 'name:' + name
		connectAs = { "type": "connect", "username": name}
		self.dSend(connectAs)
		print self.dRecieve()

		# Game parameters
		self.SCREEN_WIDTH = conf.SCREEN_WIDTH
		self.SCREEN_HEIGHT = conf.SCREEN_HEIGHT
		BG_COLOR = conf.COLOR_BG
		self.BLOCKSIZE = conf.BLOCKSIZE

		pygame.init()

		self.REST_WITH = self.SCREEN_WIDTH % self.BLOCKSIZE
		self.REST_HEIGHT = self.SCREEN_HEIGHT % self.BLOCKSIZE
		self.DRAW_RECT = pygame.Rect(0, 0, self.SCREEN_WIDTH - self.REST_WITH, self.SCREEN_HEIGHT - self.REST_HEIGHT)
		# do fancy window stuff
		pygame.display.set_caption("pyBomb")
		#pygame.display.set_icon(pygame.image.load('imgs/bandit.jpg'))
		pygame.mouse.set_visible(False)

		if not conf.FULLSCREEN:
			#os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (conf.WINDOW_POSITION_X, conf.WINDOW_POSITION_Y)
			#if not conf.WINDOW_BORDER:
			#	self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.NOFRAME, 32)

			if self.screen is None:
				self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), 0, 32)

		clock = pygame.time.Clock()
		redrawCount = 0

		keymap = {pygame.K_UP: 'w', pygame.K_RIGHT: 'd', pygame.K_DOWN: 's', pygame.K_LEFT: 'a',
		pygame.K_b: 'b'}
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
						fuseTimer = event.key -48
						print 'fusetime:',fuseTimer
					#elif event.key == pygame.K_2:  # speed up game
					#	self.gameSpeedUp()
					#elif event.key == pygame.K_1:  # slow down up game
					#	self.gameSpeedDown()
					#elif event.key == pygame.K_r:  # restart game
					#	self.resetGame()
					#	gameOver = False
					#elif event.key == pygame.K_q:
					#	self.exit_game()
					else:
						print "event.key:", event.key
					#if event.key == pygame.K_UP:
					#	self.move(1)
				else:
					pass
					#print event
			#cmds = raw_input('cmd:')
			#cmds = self.aiRand2()
			if doActions:
				doActions += 'm'

			self.screen.fill(BG_COLOR, self.DRAW_RECT)

			for cmd in doActions:
				rawSend = None
				if cmd == 'w' or cmd == 'a' or cmd == 's' or cmd == 'd':
					rawSend = { "type": "move", "direction": cmd }

				if cmd == '?':
					rawSend = { "type": "whoami" }

				if cmd == 'b':
					rawSend = { "type": "bomb", "fuse_time": fuseTimer }

				if cmd == 'm':
					rawSend = { "type": "map" }

				if cmd == '#':
					rawSend = { "type": "what_bombs" }

				if cmd == 'q':
					isRunning = False
				#{ "type": "status", "get": "X" }

				if rawSend:
					self.dSend(rawSend)

				recieved = self.dRecieve()
				if recieved and len(recieved) > 0:
					if cmd == 'm':
						#print recieved[1]
						self.drawMap(recieved[1])
					elif cmd == '#':
						print recieved
					elif cmd == '?':
						#self.client.inform("OK", [self.color, self.id, self._top, self._left])
						print 'state', 'color', 'id', 'top', 'left'
						print recieved[0], recieved[1][0], recieved[1][1], recieved[1][2], recieved[1][3]
				if redrawCount >= 10:
					# ONLY move, when the timer elapses!
					# otherwise you could change the direction multiple times before the scenery changes and upates
					# strange shit goes on!
					redrawCount = 0
				pygame.display.flip()

		self.s.close()


#clnt = client()
#clnt.run()
def multi():
	cls = client()
	cls.run()

from multiprocessing import Process

def runInParallel(*fns):
	proc = []
	for fn in fns:
		p = Process(target=fn)
		p.start()
		proc.append(p)
		time.sleep(1)

	for p in proc:
		p.join()

#runInParallel(multi, multi, multi)
multi()

#ent = raw_input('done')