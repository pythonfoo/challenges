#! /usr/bin/env python3

# pixelflut - ein grafischer Pixelflut-Client
# Copyright (C) 2014 Niklas Sombert
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys

from PySide import QtCore
from PySide import QtGui

from socket import socket
from json import JSONEncoder

class Pixelflut(QtGui.QDialog):
	def __init__(self, parent = None):
		QtGui.QDialog.__init__(self)
		form = QtGui.QFormLayout()
		self.username = QtGui.QLineEdit()
		form.addRow(self.tr("User Name"), self.username)
		self.color = QtGui.QHBoxLayout()
		self.color1 = QtGui.QLineEdit()
		self.color2 = QtGui.QLineEdit()
		self.color3 = QtGui.QLineEdit()
		self.color.addWidget(self.color1)
		self.color.addWidget(self.color2)
		self.color.addWidget(self.color3)
		form.addRow(self.tr("Color"), self.color)
		self.x = QtGui.QLineEdit()
		form.addRow(self.tr("x"), self.x)
		self.y = QtGui.QLineEdit()
		form.addRow(self.tr("y"), self.y)
		self.draw = QtGui.QPushButton("Draw")
		self.draw.clicked.connect(self.doDraw)
		self.draw.setDefault(True)
		self.answer = QtGui.QLabel()
		form.addRow(self.draw, self.answer)
		
		self.setLayout(form)
		self.json = JSONEncoder()
	

	def doDraw(self):
		try:
			s = socket()
			s.connect((sys.argv[0], int(sys.argv[1])))
			s.send(bytes(self.json.encode({"user": self.username.text(),
											   "x": int(self.x.text()),
											   "y": int(self.y.text()),
											   "color": (int(self.color1.text()),
														 int(self.color2.text()),
														 int(self.color3.text())
														)
											  }), "ASCII"))
			self.answer.setText(str(s.recv(100)))
			s.close()
		except Exception as e:
			self.answer.setText(str(e))

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	pixelflut = Pixelflut()
	pixelflut.show()
	app.exec_()

