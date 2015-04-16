__author__ = 'bison'

import time
import socket
import msgpack  # msgpack-python
import random
import os
import quoter
import control_modules
if os.path.isfile('conf_local.py'):
	import conf_local as conf
else:
	import conf


class client(object):
	def __init__(self):
		self.stillAlive = True
		self.printDebug = True
		self.printDoing = True

		self.s = socket.socket()
		self.s.settimeout(0.5)  # wait x seconds for receiving
		self.unpacker = msgpack.Unpacker()

		# bot Vars
		self.address = conf.SERVER_IP
		self.port = conf.SERVER_PORT
		self.debug('CONNECT')
		self.s.connect((self.address, self.port))
		self.debug('CONNECTED')
		#
		#self.level =
		self.chats = []

	def debug(self, txt, override=True):
		if self.printDebug or override:
			print txt

	def printDict(self, dc, sortIt=True):
		if sortIt:
			for key in dc.iterkeys():
				print key + ':', dc[key]
		else:
			for key, val in dc:
				print key + ':', val

	def dRecieve(self):
		if self.stillAlive is False:
			return False

		tmp = ''
		try:
			tmp += self.s.recv(4096)
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
		except:  # Exception as ex:
			pass

		return answer

	def dSend(self, dictData):
		if self.stillAlive is False:
			return False

		self.s.send(msgpack.dumps(dictData))

	def run(self):
		isRunning = True

		print '0: User Input'
		print "1: random 'ai'"
		print '2: ai lvl 1'
		print '3: TEST'
		gameMode = int(raw_input('select mode:'))

		controller_mod = control_modules.baseControl.baseControl()

		if gameMode == 0:
			controller_mod = control_modules.user_terminal.user_terminal()
		elif gameMode == 1:
			controller_mod = control_modules.ai_random.ai_random()
		elif gameMode == 2:
			controller_mod = control_modules.ai_lvl1.ai_lvl1()
		elif gameMode == 3:
			controller_mod = control_modules.test.test()

		#name = "bot"+str(random.randint(0,1000))
		name = conf.PLAYER_NAME  # 'bison'
		print 'name:' + name
		connectAs = {"type": "connect", "username": name, "password": conf.PLAYER_PW}
		self.dSend(connectAs)
		print self.dRecieve()

		while isRunning:
			cmds = ''

			cmds = controller_mod.getCmd()

			if cmds == '':
				cmds = ' '

			#cmds = self.aiRand2()
			for cmd in cmds:
				rawSend = None
				if cmd == 't':
					if len(self.chats) == 0:
						pass
						#quoterObj = quoter.quoter()
						#self.chats = quoterObj.loadRandomQuotes()

					if len(self.chats) > 0:
						rawSend = {"type": "shout", name + " says: ": self.chats.pop()}
					else:
						rawSend = {"type": "shout", "NOOT NOOT KEY": "NOOT NOOT VAL"}
					#rawSend = { "type": "shout", "NOOT NOOT": time.time() }

				if cmd.isdigit():
					rawSend = {"type": "set_level", "level": int(cmd)}

				if cmd == 'w':
					rawSend = {"type": "set_direction", "direction": "up"}

				if cmd == 's':
					rawSend = {"type": "set_direction", "direction": "down"}

				if cmd == 'a':
					rawSend = {"type": "set_direction", "direction": "halt"}

				if cmd == 'g':
					rawSend = {"type": "get_state"}

				if cmd == 'p':
					rawSend = {"type": "get_foo"}

				if cmd == 'h':
					rawSend = {"type": "help_command"}

				if cmd == 'p':
					rawSend = {"type": "help_plugin"}


				if cmd == 'q':
					isRunning = False

				if rawSend:
					self.dSend(rawSend)

				recieved = self.dRecieve()
				if recieved and len(recieved) > 0:
					recCmd = recieved[0]

					if recCmd == 'RESHOUT':
						if recieved[1] != conf.PLAYER_NAME:
							print recieved
					elif recCmd == 'STATUS':
						stateDict = recieved[2][0]
						#'position': 6, 'direction': 'halt', 'door': 'closed', 'passengers': []
						#print stateDict
						self.printDict(stateDict)
					elif recCmd == 'ERR':
						print 'COMMAND ERROR:', recieved
						#['ERR', '__master__', "Error while calling set_direction: do_set_level() got an unexpected keyword argument 'direction'"]
					elif recCmd == 'TRACEBACK':
						print 'SERVER ERROR:', recieved
						#['TRACEBACK', '__master__', 'Traceback (most recent call last):\n  File "/home/js/prog/hysbakstryd/hysbakstryd/network.py", line 69, in handle_msg\n    self.game.handle(self.game_client, msg_type, msg_data)\n  File "/home/js/prog/hysbakstryd/hysbakstryd/game.py", line 200, in handle\n    ret = self.command_map[msg_type](client, **msg_data)\n  File "/home/js/prog/hysbakstryd/hysbakstryd/game.py", line 184, in <lambda>\n    self.command_map[command_method_name[3:]] = lambda *args, **kwargs: getattr(plugin, command_method_name)(plugin, *args, **kwargs)\nTypeError: do_set_level() got an unexpected keyword argument \'direction\'\n']
					else:
						print 'unknown:', recCmd, recieved

					if cmd == 'm':
						print recieved[1]
					elif cmd == '#':
						print recieved
					elif cmd == '?':
						pass
						#self.client.inform("OK", [self.color, self.id, self._top, self._left])
						#print 'state', 'color', 'id', 'top', 'left'
						#print recieved[0], recieved[1][0], recieved[1][1], recieved[1][2], recieved[1][3]

		self.s.close()


cls = client()
cls.run()