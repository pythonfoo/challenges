import baseControl
import time
import random


class test_all(baseControl.baseControl):
	def __init__(self):
		super(test_all, self).__init__()
		#self.actions = '123456789wfg fg fg fg fg fg fg fg fg fg 876543210sfg fg fg fg fg fg fg fg fg fg fg fg' #'1w2w3w4w5w6w7w8w9w0s9s8s7s6s5s4s3s2s1' #'123456789w          876543210s           '
		self.actions = 'gftw 123456789 m      gft      s 876543210 m      gft      '
		self.actionIndex = -1

	def getCmd(self):
		self.actionIndex += 1
		if self.actionIndex >= len(self.actions):
			self.actionIndex = 0

		action = self.actions[self.actionIndex]
		if action == 'w' or action == 's' or action == 'm':
			time.sleep(0.05)
		elif action == ' ':
			time.sleep(2)
		else:
			time.sleep(0.01)

		print 'ACTION: "' + action + '" index:' + str(self.actionIndex)
		return action