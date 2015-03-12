import baseControl
import time
import random


class test(baseControl.baseControl):
	def __init__(self):
		super(test, self).__init__()
		self.actions = 'hp'  #'5gwgagtg1gsgtg'
		self.actionIndex = -1

	def getCmd(self):
		time.sleep(random.uniform(0.1, 5.0))
		self.actionIndex += 1
		if self.actionIndex >= len(self.actions):
			self.actionIndex = 0

		return random.choice(self.actions[self.actionIndex])