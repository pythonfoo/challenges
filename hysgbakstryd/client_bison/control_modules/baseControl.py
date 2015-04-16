class baseControl(object):
	def __init__(self):
		self.lastMap = ''

	def setRawReceived(self, received):
		pass

	def setReceived(self, cmdName, received):
		pass

	def getCmd(self):
		return ''