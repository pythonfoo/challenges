__author__ = 'bison'

import time
import socket
import msgpack
import random
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
		actions = ['w', 'b']
		return random.choice(actions)

	def run(self):
		isRunning = True
		name = "bot"+str(random.randint(0,1000))
		name = 'bison'
		print 'name:' + name
		connectAs = { "type": "connect", "username": name}
		self.dSend(connectAs)
		print self.dRecieve()

		while isRunning:
			#cmds = raw_input('cmd:')
			cmds = self.aiRand2()
			for cmd in cmds:
				rawSend = None
				if cmd == 'w' or cmd == 'a' or cmd == 's' or cmd == 'd':
					rawSend = { "type": "move", "direction": cmd }

				if cmd == '?':
					rawSend = { "type": "whoami" }

				if cmd == 'b':
					rawSend = { "type": "bomb", "fuse_time": 5 }

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
						print recieved[1]
					elif cmd == '#':
						print recieved
					elif cmd == '?':
						#self.client.inform("OK", [self.color, self.id, self._top, self._left])
						print 'state', 'color', 'id', 'top', 'left'
						print recieved[0], recieved[1][0], recieved[1][1], recieved[1][2], recieved[1][3]

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

ent = raw_input('done')