__author__ = 'bison'

import time
import socket
import msgpack
#msgpack-python

class client(object):
	def __init__(self):
		self.stillAlive = True
		self.printDebug = True
		self.printDoing = True

		self.s = socket.socket()
		self.s.settimeout(0.1) # wait x seconds for recieving
		self.socketEmptyCounter = 0 # Scoket disconnect fix!
		self.cBuffer = []
		self.pingTimerLast = time.time()
		self.pingServerLast = time.time()
		self.pingInterval = 10.0
		self.command = ''
		self.commandIsLocked = False

		# bot Vars
		self.address = '172.22.27.191'
		self.port = 8001
		self.s.connect((self.address, self.port))

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
				self.debug('|incomplete command: ' + tmp, True)

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

	def run(self):
		isRunning = True
		while isRunning:
			cmd = raw_input('cmd:')
			rawSend = None
			if cmd == 'w' or cmd == 'a' or cmd == 's' or cmd == 'd':
				rawSend = { "type": "move", "direction": cmd }

			if cmd == '?':
				rawSend = { "type": "whoami" }

			if cmd == 'b':
				rawSend = { "type": "action", "set": "bomb" }

			if cmd == 'q':
				isRunning = False
			#{ "type": "status", "get": "X" }

			if rawSend:
				self.dSend(rawSend)

			recieved = self.dRecieve()
			if recieved:
				if cmd == '?':
					#self.client.inform("OK", [self.color, self.id, self._top, self._left])
					print 'state', 'color', 'id', 'top', 'left'
					print recieved[0], recieved[1][0], recieved[1][1], recieved[1][2], recieved[1][3]

		self.s.close()


clnt = client()
clnt.run()