__author__ = 'bison'

import time
import socket
import msgpack  # msgpack-python
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
		self.loadQuotes = False

		self.doConnect()
		'''
		self.s = socket.socket()
		self.s.settimeout(0.5)  # wait x seconds for receiving
		self.unpacker = msgpack.Unpacker()

		# config Vars
		self.address = conf.SERVER_IP
		self.port = conf.SERVER_PORT
		self.debug('CONNECT')
		self.s.connect((self.address, self.port))
		self.debug('CONNECTED')
		#
		#self.level =
		self.chats = []'''

	def doConnect(self):
		self.s = socket.socket()
		self.s.settimeout(0.5)  # wait x seconds for receiving
		self.unpacker = msgpack.Unpacker()

		# config Vars
		self.address = conf.SERVER_IP
		self.port = conf.SERVER_PORT
		self.debug('CONNECT')
		self.s.connect((self.address, self.port))
		self.debug('CONNECTED')
		#
		#self.level =
		self.chats = []

	def debug(self, *vars):
		if self.printDebug:
			print time.time(), ':', vars

	def getDictAsString(self, dc, sortIt=True):
		finalStr = ''
		if sortIt:
			for key in dc.iterkeys():
				finalStr += key + ':' + str(dc[key]) + "\n"
		else:
			for key, val in dc:
				finalStr += key + ':' + str(val) + "\n"
		return finalStr

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
			self.debug('Recieved UNKNOWN ERROR (LEAVING): ' + str(e))

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
		print '4: TEST ALL'
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
		elif gameMode == 4:
			controller_mod = control_modules.test_all.test_all()


		while isRunning:
			try:
				#name = "bot"+str(random.randint(0,1000))
				name = conf.PLAYER_NAME  # 'bison'
				print 'name:' + name
				connectAs = {"type": "connect", "username": name, "password": conf.PLAYER_PW}
				self.dSend(connectAs)
				#['LOGGEDIN', '__master__', {'msg': 'You have logged in and are inactive. When you want to start playing, send `activate`.', 'username': 'bison'}]
				print self.dRecieve()

				activate = {"type": "activate"}
				self.dSend(activate)
				#['activated', '__master__', {'msg': 'A shaft was built for you. You can transport now.'}]
				print self.dRecieve()

				self.s.settimeout(0.2)
				while isRunning:
					cmds = ''

					cmds = controller_mod.getCmd()

					if cmds == '':
						# we need at least one char to call the reciee function
						cmds = ' '

					#cmds = self.aiRand2()
					for cmd in cmds:
						rawSend = None
						if cmd == 't':
							if len(self.chats) == 0:
								if self.loadQuotes:
									quoterObj = quoter.quoter()
									self.chats = quoterObj.loadRandomQuotes()

							if len(self.chats) > 0:
								rawSend = {"type": "shout", name + " says: ": self.chats.pop()}
							else:
								rawSend = {"type": "shout", "NOOT NOOT KEY": "NOOT NOOT VAL"}
							#rawSend = { "type": "shout", "NOOT NOOT": time.time() }

						if cmd.isdigit():
							floor = int(cmd)
							rawSend = {"type": "set_level", "level": floor}

						if cmd == 'g':
							rawSend = {"type": "get_state"}

						if cmd == 'f':
							rawSend = {"type": "get_world_state"}

						if cmd == 'w':
							rawSend = {"type": "set_direction", "direction": "up"}

						if cmd == 's':
							rawSend = {"type": "set_direction", "direction": "down"}

						if cmd == 'a':
							rawSend = {"type": "set_direction", "direction": "halt"}

						if cmd == 'm':
							rawSend = {"type": "move"}
						#if cmd == 'g':
						#	rawSend = {"type": "get_state"}

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

							controller_mod.setRawReceived(recieved)
							controller_mod.setReceived(recCmd, recieved)

							#self.debug('RECIEVED: CMD: "', recCmd, '" -> DATA: ', recieved)

							if recCmd == 'RESHOUT':
								if recieved[1] != conf.PLAYER_NAME:
									self.debug(recieved)

							elif recCmd == 'state' or recCmd == 'WORLD_STATE':
								pass
								#stateDict = recieved[2]
								#self.debug(recCmd, stateDict)
								#['state', '__master__', {'username': 'bison', 'direction': 'halt', 'movement_paused': False, 'door': 'closed', 'level': 0.0, 'levels': [5]}]
								#{'gglptdn': {'username': 'gglptdn', 'direction': 'halt', 'movement_paused': False, 'door': 'closed', 'level': 9, 'people_transported': 16, 'on_board': [], '_stopped_at': 6915, 'levels': [], '_resume_at': 6925}, '__world__': {'waiting_down': {'1': [], '0': [], '3': [{'appeared_in': 3, 'direction': 'down', 'type': 'm', 'id': 802, 'appeared_time': 9520}, {'appeared_in': 3, 'direction': 'down', 'type': 'f', 'id': 803, 'appeared_time': 9523}, {'appeared_in': 3, 'direction': 'down', 'type': 'f', 'id': 815, 'appeared_time': 9670}, {'appeared_in': 3, 'direction': 'down', 'type': 'm', 'id': 816, 'appeared_time': 9684}], '2': [{'appeared_in': 2, 'direction': 'down', 'type': 'm', 'id': 818, 'appeared_time': 9728}, {'appeared_in': 2, 'direction': 'down', 'type': 'm', 'id': 826, 'appeared_time': 10082}, {'appeared_in': 2, 'direction': 'down', 'type': 'm', 'id': 867, 'appeared_time': 12722}], '5': [{'appeared_in': 5, 'direction': 'down', 'type': 'f', 'id': 787, 'appeared_time': 9427}, {'appeared_in': 5, 'direction': 'down', 'type': 'f', 'id': 788, 'appeared_time': 9430}, {'appeared_in': 5, 'direction': 'down', 'type': 'f', 'id': 793, 'appeared_time': 9450}, {'appeared_in': 5, 'direction': 'down', 'type': 'm', 'id': 810, 'appeared_time': 9592}, {'appeared_in': 5, 'direction': 'down', 'type': 'f', 'id': 814, 'appeared_time': 9654}, {'appeared_in': 5, 'direction': 'down', 'type': 'f', 'id': 817, 'appeared_time': 9721}, {'appeared_in': 5, 'direction': 'down', 'type': 'm', 'id': 823, 'appeared_time': 9821}, {'appeared_in': 5, 'direction': 'down', 'type': 'm', 'id': 829, 'appeared_time': 10172}, {'appeared_in': 5, 'direction': 'down', 'type': 'm', 'id': 836, 'appeared_time': 10654}, {'appeared_in': 5, 'direction': 'down', 'type': 'm', 'id': 842, 'appeared_time': 11022}], '4': [{'appeared_in': 4, 'direction': 'down', 'type': 'm', 'id': 723, 'appeared_time': 9086}, {'appeared_in': 4, 'direction': 'down', 'type': 'f', 'id': 724, 'appeared_time': 9098}, {'appeared_in': 4, 'direction': 'down', 'type': 'm_child', 'id': 725, 'appeared_time': 9101}, {'appeared_in': 4, 'direction': 'down', 'type': 'm', 'id': 742, 'appeared_time': 9193}, {'appeared_in': 4, 'direction': 'down', 'type': 'm', 'id': 768, 'appeared_time': 9303}, {'appeared_in': 4, 'direction': 'down', 'type': 'f', 'id': 798, 'appeared_time': 9488}, {'appeared_in': 4, 'direction': 'down', 'type': 'f', 'id': 808, 'appeared_time': 9587}, {'appeared_in': 4, 'direction': 'down', 'type': 'f_child', 'id': 812, 'appeared_time': 9611}, {'appeared_in': 4, 'direction': 'down', 'type': 'f_child', 'id': 813, 'appeared_time': 9632}, {'appeared_in': 4, 'direction': 'down', 'type': 'm', 'id': 825, 'appeared_time': 10022}, {'appeared_in': 4, 'direction': 'down', 'type': 'm', 'id': 828, 'appeared_time': 10164}, {'appeared_in': 4, 'direction': 'down', 'type': 'f', 'id': 851, 'appeared_time': 11815}], '7': [{'appeared_in': 7, 'direction': 'down', 'type': 'm', 'id': 761, 'appeared_time': 9279}, {'appeared_in': 7, 'direction': 'down', 'type': 'm', 'id': 775, 'appeared_time': 9351}, {'appeared_in': 7, 'direction': 'down', 'type': 'm', 'id': 780, 'appeared_time': 9382}, {'appeared_in': 7, 'direction': 'down', 'type': 'm', 'id': 791, 'appeared_time': 9440}, {'appeared_in': 7, 'direction': 'down', 'type': 'f', 'id': 805, 'appeared_time': 9534}, {'appeared_in': 7, 'direction': 'down', 'type': 'f', 'id': 822, 'appeared_time': 9810}, {'appeared_in': 7, 'direction': 'down', 'type': 'm', 'id': 824, 'appeared_time': 9831}, {'appeared_in': 7, 'direction': 'down', 'type': 'm_child', 'id': 852, 'appeared_time': 11821}], '6': [{'appeared_in': 6, 'direction': 'down', 'type': 'm_child', 'id': 781, 'appeared_time': 9396}, {'appeared_in': 6, 'direction': 'down', 'type': 'f', 'id': 789, 'appeared_time': 9436}, {'appeared_in': 6, 'direction': 'down', 'type': 'f', 'id': 795, 'appeared_time': 9454}, {'appeared_in': 6, 'direction': 'down', 'type': 'f_child', 'id': 820, 'appeared_time': 9772}, {'appeared_in': 6, 'direction': 'down', 'type': 'f', 'id': 833, 'appeared_time': 10368}, {'appeared_in': 6, 'direction': 'down', 'type': 'f', 'id': 840, 'appeared_time': 10802}, {'appeared_in': 6, 'direction': 'down', 'type': 'm', 'id': 841, 'appeared_time': 10813}, {'appeared_in': 6, 'direction': 'down', 'type': 'm', 'id': 858, 'appeared_time': 12222}, {'appeared_in': 6, 'direction': 'down', 'type': 'm', 'id': 875, 'appeared_time': 13130}], '9': [{'appeared_in': 9, 'direction': 'down', 'type': 'm_child', 'id': 854, 'appeared_time': 11895}, {'appeared_in': 9, 'direction': 'down', 'type': 'f', 'id': 856, 'appeared_time': 12121}, {'appeared_in': 9, 'direction': 'down', 'type': 'm', 'id': 857, 'appeared_time': 12191}, {'appeared_in': 9, 'direction': 'down', 'type': 'm', 'id': 870, 'appeared_time': 12927}, {'appeared_in': 9, 'direction': 'down', 'type': 'm_child', 'id': 873, 'appeared_time': 13016}], '8': [{'appeared_in': 8, 'direction': 'down', 'type': 'f', 'id': 636, 'appeared_time': 8474}, {'appeared_in': 8, 'direction': 'down', 'type': 'f', 'id': 665, 'appeared_time': 8780}, {'appeared_in': 8, 'direction': 'down', 'type': 'f', 'id': 666, 'appeared_time': 8786}, {'appeared_in': 8, 'direction': 'down', 'type': 'm', 'id': 679, 'appeared_time': 8887}, {'appeared_in': 8, 'direction': 'down', 'type': 'm', 'id': 690, 'appeared_time': 8940}, {'appeared_in': 8, 'direction': 'down', 'type': 'f', 'id': 702, 'appeared_time': 8985}, {'appeared_in': 8, 'direction': 'down', 'type': 'f', 'id': 754, 'appeared_time': 9252}, {'appeared_in': 8, 'direction': 'down', 'type': 'm', 'id': 766, 'appeared_time': 9292}, {'appeared_in': 8, 'direction': 'down', 'type': 'm', 'id': 767, 'appeared_time': 9296}, {'appeared_in': 8, 'direction': 'down', 'type': 'f', 'id': 770, 'appeared_time': 9328}, {'appeared_in': 8, 'direction': 'down', 'type': 'f', 'id': 786, 'appeared_time': 9423}, {'appeared_in': 8, 'direction': 'down', 'type': 'f', 'id': 790, 'appeared_time': 9438}, {'appeared_in': 8, 'direction': 'down', 'type': 'm_child', 'id': 796, 'appeared_time': 9474}, {'appeared_in': 8, 'direction': 'down', 'type': 'f', 'id': 797, 'appeared_time': 9487}, {'appeared_in': 8, 'direction': 'down', 'type': 'f', 'id': 806, 'appeared_time': 9558}, {'appeared_in': 8, 'direction': 'down', 'type': 'f', 'id': 835, 'appeared_time': 10560}, {'appeared_in': 8, 'direction': 'down', 'type': 'f', 'id': 848, 'appeared_time': 11596}, {'appeared_in': 8, 'direction': 'down', 'type': 'm', 'id': 859, 'appeared_time': 12243}, {'appeared_in': 8, 'direction': 'down', 'type': 'f', 'id': 866, 'appeared_time': 12619}]}, 'people_transported': 621, 'waiting_up': {'1': [{'appeared_in': 1, 'direction': 'up', 'type': 'f', 'id': 511, 'appeared_time': 7503}, {'appeared_in': 1, 'direction': 'up', 'type': 'm', 'id': 544, 'appeared_time': 7757}, {'appeared_in': 1, 'direction': 'up', 'type': 'm', 'id': 546, 'appeared_time': 7772}, {'appeared_in': 1, 'direction': 'up', 'type': 'm_child', 'id': 551, 'appeared_time': 7815}, {'appeared_in': 1, 'direction': 'up', 'type': 'm', 'id': 560, 'appeared_time': 7875}, {'appeared_in': 1, 'direction': 'up', 'type': 'm', 'id': 564, 'appeared_time': 7902}, {'appeared_in': 1, 'direction': 'up', 'type': 'm', 'id': 580, 'appeared_time': 8001}, {'appeared_in': 1, 'direction': 'up', 'type': 'm', 'id': 590, 'appeared_time': 8059}, {'appeared_in': 1, 'direction': 'up', 'type': 'm', 'id': 592, 'appeared_time': 8068}, {'appeared_in': 1, 'direction': 'up', 'type': 'm', 'id': 613, 'appeared_time': 8270}, {'appeared_in': 1, 'direction': 'up', 'type': 'f_child', 'id': 617, 'appeared_time': 8318}, {'appeared_in': 1, 'direction': 'up', 'type': 'f', 'id': 648, 'appeared_time': 8631}, {'appeared_in': 1, 'direction': 'up', 'type': 'f', 'id': 663, 'appeared_time': 8762}, {'appeared_in': 1, 'direction': 'up', 'type': 'f', 'id': 678, 'appeared_time': 8876}, {'appeared_in': 1, 'direction': 'up', 'type': 'f', 'id': 701, 'appeared_time': 8975}, {'appeared_in': 1, 'direction': 'up', 'type': 'm', 'id': 739, 'appeared_time': 9178}, {'appeared_in': 1, 'direction': 'up', 'type': 'm', 'id': 834, 'appeared_time': 10391}, {'appeared_in': 1, 'direction': 'up', 'type': 'f', 'id': 847, 'appeared_time': 11322}, {'appeared_in': 1, 'direction': 'up', 'type': 'f', 'id': 853, 'appeared_time': 11850}, {'appeared_in': 1, 'direction': 'up', 'type': 'm', 'id': 861, 'appeared_time': 12445}, {'appeared_in': 1, 'direction': 'up', 'type': 'm', 'id': 868, 'appeared_time': 12778}, {'appeared_in': 1, 'direction': 'up', 'type': 'f', 'id': 871, 'appeared_time': 12928}, {'appeared_in': 1, 'direction': 'up', 'type': 'm', 'id': 872, 'appeared_time': 12984}, {'appeared_in': 1, 'direction': 'up', 'type': 'f_child', 'id': 874, 'appeared_time': 13032}, {'appeared_in': 1, 'direction': 'up', 'type': 'f', 'id': 876, 'appeared_time': 13141}, {'appeared_in': 1, 'direction': 'up', 'type': 'f', 'id': 878, 'appeared_time': 13167}], '0': [{'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 189, 'appeared_time': 4089}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 190, 'appeared_time': 4092}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 191, 'appeared_time': 4097}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 192, 'appeared_time': 4101}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 193, 'appeared_time': 4102}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 201, 'appeared_time': 4440}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 202, 'appeared_time': 4444}, {'appeared_in': 0, 'direction': 'up', 'type': 'm_child', 'id': 203, 'appeared_time': 4449}, {'appeared_in': 0, 'direction': 'up', 'type': 'f_child', 'id': 204, 'appeared_time': 4450}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 215, 'appeared_time': 4726}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 216, 'appeared_time': 4729}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 217, 'appeared_time': 4731}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 218, 'appeared_time': 4733}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 235, 'appeared_time': 5062}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 242, 'appeared_time': 5178}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 247, 'appeared_time': 5206}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 250, 'appeared_time': 5220}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 294, 'appeared_time': 5652}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 298, 'appeared_time': 5675}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 307, 'appeared_time': 5722}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 313, 'appeared_time': 5765}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 323, 'appeared_time': 5899}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 324, 'appeared_time': 5905}, {'appeared_in': 0, 'direction': 'up', 'type': 'm_child', 'id': 325, 'appeared_time': 5908}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 326, 'appeared_time': 5917}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 377, 'appeared_time': 6363}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 398, 'appeared_time': 6482}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 407, 'appeared_time': 6562}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 414, 'appeared_time': 6596}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 423, 'appeared_time': 6671}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 430, 'appeared_time': 6720}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 431, 'appeared_time': 6739}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 433, 'appeared_time': 6753}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 445, 'appeared_time': 6861}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 469, 'appeared_time': 7091}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 470, 'appeared_time': 7097}, {'appeared_in': 0, 'direction': 'up', 'type': 'm_child', 'id': 473, 'appeared_time': 7121}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 482, 'appeared_time': 7212}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 490, 'appeared_time': 7299}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 491, 'appeared_time': 7321}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 493, 'appeared_time': 7367}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 495, 'appeared_time': 7375}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 497, 'appeared_time': 7386}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 504, 'appeared_time': 7450}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 515, 'appeared_time': 7531}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 520, 'appeared_time': 7561}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 527, 'appeared_time': 7604}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 538, 'appeared_time': 7682}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 539, 'appeared_time': 7688}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 562, 'appeared_time': 7894}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 586, 'appeared_time': 8039}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 593, 'appeared_time': 8073}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 597, 'appeared_time': 8086}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 603, 'appeared_time': 8198}, {'appeared_in': 0, 'direction': 'up', 'type': 'm_child', 'id': 610, 'appeared_time': 8251}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 616, 'appeared_time': 8311}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 622, 'appeared_time': 8374}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 659, 'appeared_time': 8742}, {'appeared_in': 0, 'direction': 'up', 'type': 'm_child', 'id': 669, 'appeared_time': 8822}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 684, 'appeared_time': 8916}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 689, 'appeared_time': 8935}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 695, 'appeared_time': 8955}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 705, 'appeared_time': 8996}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 722, 'appeared_time': 9085}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 733, 'appeared_time': 9151}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 763, 'appeared_time': 9283}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 774, 'appeared_time': 9350}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 782, 'appeared_time': 9397}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 783, 'appeared_time': 9404}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 838, 'appeared_time': 10684}, {'appeared_in': 0, 'direction': 'up', 'type': 'm', 'id': 860, 'appeared_time': 12274}, {'appeared_in': 0, 'direction': 'up', 'type': 'f', 'id': 865, 'appeared_time': 12616}], '3': [{'appeared_in': 3, 'direction': 'up', 'type': 'f', 'id': 443, 'appeared_time': 6848}, {'appeared_in': 3, 'direction': 'up', 'type': 'm', 'id': 447, 'appeared_time': 6865}, {'appeared_in': 3, 'direction': 'up', 'type': 'f', 'id': 484, 'appeared_time': 7251}, {'appeared_in': 3, 'direction': 'up', 'type': 'f', 'id': 526, 'appeared_time': 7598}, {'appeared_in': 3, 'direction': 'up', 'type': 'f', 'id': 529, 'appeared_time': 7606}, {'appeared_in': 3, 'direction': 'up', 'type': 'f', 'id': 536, 'appeared_time': 7650}, {'appeared_in': 3, 'direction': 'up', 'type': 'm', 'id': 537, 'appeared_time': 7660}, {'appeared_in': 3, 'direction': 'up', 'type': 'm', 'id': 548, 'appeared_time': 7790}, {'appeared_in': 3, 'direction': 'up', 'type': 'f', 'id': 571, 'appeared_time': 7943}, {'appeared_in': 3, 'direction': 'up', 'type': 'f', 'id': 576, 'appeared_time': 7985}, {'appeared_in': 3, 'direction': 'up', 'type': 'm', 'id': 606, 'appeared_time': 8208}, {'appeared_in': 3, 'direction': 'up', 'type': 'm', 'id': 614, 'appeared_time': 8272}, {'appeared_in': 3, 'direction': 'up', 'type': 'm', 'id': 623, 'appeared_time': 8385}, {'appeared_in': 3, 'direction': 'up', 'type': 'f', 'id': 634, 'appeared_time': 8462}, {'appeared_in': 3, 'direction': 'up', 'type': 'm', 'id': 658, 'appeared_time': 8733}, {'appeared_in': 3, 'direction': 'up', 'type': 'm', 'id': 671, 'appeared_time': 8835}, {'appeared_in': 3, 'direction': 'up', 'type': 'm', 'id': 843, 'appeared_time': 11027}, {'appeared_in': 3, 'direction': 'up', 'type': 'f', 'id': 849, 'appeared_time': 11608}, {'appeared_in': 3, 'direction': 'up', 'type': 'm', 'id': 869, 'appeared_time': 12911}, {'appeared_in': 3, 'direction': 'up', 'type': 'f', 'id': 880, 'appeared_time': 13264}], '2': [{'appeared_in': 2, 'direction': 'up', 'type': 'm', 'id': 436, 'appeared_time': 6776}, {'appeared_in': 2, 'direction': 'up', 'type': 'f', 'id': 444, 'appeared_time': 6857}, {'appeared_in': 2, 'direction': 'up', 'type': 'f_child', 'id': 468, 'appeared_time': 7069}, {'appeared_in': 2, 'direction': 'up', 'type': 'm', 'id': 496, 'appeared_time': 7384}, {'appeared_in': 2, 'direction': 'up', 'type': 'm', 'id': 498, 'appeared_time': 7389}, {'appeared_in': 2, 'direction': 'up', 'type': 'f', 'id': 522, 'appeared_time': 7563}, {'appeared_in': 2, 'direction': 'up', 'type': 'f', 'id': 553, 'appeared_time': 7844}, {'appeared_in': 2, 'direction': 'up', 'type': 'f', 'id': 577, 'appeared_time': 7987}, {'appeared_in': 2, 'direction': 'up', 'type': 'm', 'id': 578, 'appeared_time': 7996}, {'appeared_in': 2, 'direction': 'up', 'type': 'f', 'id': 642, 'appeared_time': 8557}, {'appeared_in': 2, 'direction': 'up', 'type': 'f_child', 'id': 646, 'appeared_time': 8601}, {'appeared_in': 2, 'direction': 'up', 'type': 'm', 'id': 651, 'appeared_time': 8664}, {'appeared_in': 2, 'direction': 'up', 'type': 'f', 'id': 657, 'appeared_time': 8729}, {'appeared_in': 2, 'direction': 'up', 'type': 'm', 'id': 676, 'appeared_time': 8861}, {'appeared_in': 2, 'direction': 'up', 'type': 'm', 'id': 819, 'appeared_time': 9732}, {'appeared_in': 2, 'direction': 'up', 'type': 'm', 'id': 827, 'appeared_time': 10147}, {'appeared_in': 2, 'direction': 'up', 'type': 'f', 'id': 831, 'appeared_time': 10350}, {'appeared_in': 2, 'direction': 'up', 'type': 'm', 'id': 846, 'appeared_time': 11321}, {'appeared_in': 2, 'direction': 'up', 'type': 'm_child', 'id': 850, 'appeared_time': 11724}, {'appeared_in': 2, 'direction': 'up', 'type': 'f', 'id': 862, 'appeared_time': 12453}, {'appeared_in': 2, 'direction': 'up', 'type': 'm', 'id': 863, 'appeared_time': 12472}, {'appeared_in': 2, 'direction': 'up', 'type': 'f', 'id': 879, 'appeared_time': 13226}], '5': [{'appeared_in': 5, 'direction': 'up', 'type': 'f', 'id': 574, 'appeared_time': 7971}, {'appeared_in': 5, 'direction': 'up', 'type': 'm', 'id': 575, 'appeared_time': 7978}, {'appeared_in': 5, 'direction': 'up', 'type': 'm', 'id': 596, 'appeared_time': 8081}, {'appeared_in': 5, 'direction': 'up', 'type': 'm', 'id': 626, 'appeared_time': 8398}, {'appeared_in': 5, 'direction': 'up', 'type': 'f', 'id': 627, 'appeared_time': 8408}, {'appeared_in': 5, 'direction': 'up', 'type': 'f', 'id': 633, 'appeared_time': 8453}, {'appeared_in': 5, 'direction': 'up', 'type': 'm', 'id': 641, 'appeared_time': 8519}, {'appeared_in': 5, 'direction': 'up', 'type': 'm', 'id': 708, 'appeared_time': 9028}, {'appeared_in': 5, 'direction': 'up', 'type': 'f', 'id': 830, 'appeared_time': 10304}], '4': [{'appeared_in': 4, 'direction': 'up', 'type': 'm', 'id': 494, 'appeared_time': 7373}, {'appeared_in': 4, 'direction': 'up', 'type': 'm', 'id': 509, 'appeared_time': 7488}, {'appeared_in': 4, 'direction': 'up', 'type': 'm', 'id': 524, 'appeared_time': 7587}, {'appeared_in': 4, 'direction': 'up', 'type': 'f', 'id': 563, 'appeared_time': 7900}, {'appeared_in': 4, 'direction': 'up', 'type': 'f', 'id': 629, 'appeared_time': 8420}, {'appeared_in': 4, 'direction': 'up', 'type': 'm', 'id': 637, 'appeared_time': 8497}, {'appeared_in': 4, 'direction': 'up', 'type': 'm', 'id': 640, 'appeared_time': 8516}, {'appeared_in': 4, 'direction': 'up', 'type': 'f', 'id': 662, 'appeared_time': 8757}, {'appeared_in': 4, 'direction': 'up', 'type': 'm', 'id': 664, 'appeared_time': 8773}, {'appeared_in': 4, 'direction': 'up', 'type': 'm', 'id': 691, 'appeared_time': 8943}, {'appeared_in': 4, 'direction': 'up', 'type': 'f', 'id': 714, 'appeared_time': 9050}, {'appeared_in': 4, 'direction': 'up', 'type': 'm', 'id': 837, 'appeared_time': 10660}, {'appeared_in': 4, 'direction': 'up', 'type': 'f_child', 'id': 844, 'appeared_time': 11176}, {'appeared_in': 4, 'direction': 'up', 'type': 'm', 'id': 855, 'appeared_time': 11902}, {'appeared_in': 4, 'direction': 'up', 'type': 'f', 'id': 877, 'appeared_time': 13151}], '7': [], '6': [], '9': [], '8': []}, 'time': 13334}, 'hwm': {'username': 'hwm', 'direction': 'up', 'movement_paused': False, 'door': 'open', 'level': 8, 'people_transported': 161, 'on_board': [], '_stopped_at': 13323, 'levels': [], '_resume_at': 13333}, 'shezi': {'username': 'shezi', 'direction': 'down', 'movement_paused': False, 'door': 'open', 'level': 1, 'people_transported': 258, 'on_board': [{'direction': 'down', 'wants_to': 0, 'appeared_time': 9506, 'appeared_in': 9, 'type': 'f', 'id': 801}, {'direction': 'down', 'wants_to': 0, 'appeared_time': 9380, 'appeared_in': 6, 'type': 'f', 'id': 779}], '_stopped_at': 13331, 'levels': [0], '_resume_at': 13341}, 'bison': {'username': 'bison', 'direction': 'halt', 'movement_paused': False, 'door': 'closed', 'level': 0, 'people_transported': 12, 'on_board': [], '_stopped_at': 12925, 'levels': [1, 2, 3, 4, 5, 6, 7, 8, 9, 0], '_resume_at': 10}})
								#'position': 6, 'direction': 'halt', 'door': 'closed', 'passengers': []
								#print stateDict
								#self.debug('state:', self.getDictAsString(stateDict))

							elif recCmd == 'help_for_commands' or recCmd == 'help_for_plugins':
								self.debug(recieved)
								#unknown: help_for_commands ['help_for_commands', '__master__', ['shout', 'reset_levels', 'set_direction', 'help_command', 'set_level', 'help_plugin']]
								#unknown: help_for_plugins ['help_for_plugins', '__master__', ['MovementPhase1', 'ShoutPlugin', 'HelpPlugin']]
							elif recCmd == 'ERR':
								self.debug('COMMAND ERROR:', recieved)
								#['ERR', '__master__', "Error while calling set_direction: do_set_level() got an unexpected keyword argument 'direction'"]
							elif recCmd == 'TRACEBACK':
								self.debug('SERVER ERROR:', recieved)
								#['TRACEBACK', '__master__', 'Traceback (most recent call last):\n  File "/home/js/prog/hysbakstryd/hysbakstryd/network.py", line 69, in handle_msg\n    self.game.handle(self.game_client, msg_type, msg_data)\n  File "/home/js/prog/hysbakstryd/hysbakstryd/game.py", line 200, in handle\n    ret = self.command_map[msg_type](client, **msg_data)\n  File "/home/js/prog/hysbakstryd/hysbakstryd/game.py", line 184, in <lambda>\n    self.command_map[command_method_name[3:]] = lambda *args, **kwargs: getattr(plugin, command_method_name)(plugin, *args, **kwargs)\nTypeError: do_set_level() got an unexpected keyword argument \'direction\'\n']

							elif recCmd == 'LEVELS':
								pass
								#self.debug('LEVELS:', recieved)
								#['LEVELS', 'bison', [1, 2, 3, 4]]

							elif recCmd == 'DIRECTION':
								pass
								#self.debug('DIRECTION:', recieved)
								#['DIRECTION', 'hwm', 'up']

							elif recCmd == 'disembarking':
								pass
								# ['disembarking', '__master__', []]

							elif recCmd == 'DOORS CLOSED' or recCmd == 'DOORS OPENED':
								pass
								#self.debug('DOORS:', recieved)
								#['DOORS OPENED', '__master__', ['bison', 3]]
								#['DOORS CLOSED', '__master__', ['bison', 3]]

							elif recCmd == 'person_boards':
								pass
								#['person_boards', '__master__', {'direction': 'up', 'wants_to': 8, 'appeared_time': 13443, 'appeared_in': 7, 'type': 'f', 'id': 883}])

							elif recCmd == 'activated':
								pass
								#['activated', '__master__', {'msg': 'A shaft was built for you. You can transport now.'}]

							elif recCmd == 'STOPPED':
								pass
								#['STOPPED', '__master__', ['bison', 0.0]]

							elif recCmd == 'WELCOME':
								pass
								#self.debug('WELCOME:', recieved)
								#['WELCOME', '__master__', 'bison']

							else:
								self.debug('unknown:', recCmd, recieved)

							if cmd == 'm':
								print recieved[1]
							elif cmd == '#':
								print recieved
							elif cmd == '?':
								pass
								#self.client.inform("OK", [self.color, self.id, self._top, self._left])
								#print 'state', 'color', 'id', 'top', 'left'
								#print recieved[0], recieved[1][0], recieved[1][1], recieved[1][2], recieved[1][3]
			except Exception as ex:
				self.debug('CON ERROR: ', ex)
				self.doDisconnect()
				time.sleep(1)
				self.doConnect()

		self.doDisconnect()

	def doDisconnect(self):
		try:
			self.s.close()
		except Exception as ex:
			self.debug('doDisconnect ERROR: ' + str(ex))

cls = client()
cls.run()