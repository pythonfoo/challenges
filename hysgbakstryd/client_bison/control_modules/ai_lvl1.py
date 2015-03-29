import baseControl
import time
import random


class ai_lvl1(baseControl.baseControl):
	def __init__(self):
		super(ai_lvl1, self).__init__()
		self.actions = 'wwwsssaaagggpppttt0123456789        '

	def getCmd(self):
		time.sleep(random.uniform(0.1, 5.0))
		return random.choice(self.actions)