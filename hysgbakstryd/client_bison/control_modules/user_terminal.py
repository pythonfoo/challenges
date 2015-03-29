import baseControl


class user_terminal(baseControl.baseControl):
	def __init__(self):
		super(user_terminal, self).__init__()

	def getCmd(self):
		return raw_input('cmd:')