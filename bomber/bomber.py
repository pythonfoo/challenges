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

from socket import socket
from msgpack import packb, unpackb
from msgpack.exceptions import UnpackValueError
from random import choice

class Bomber:
	def __init__(self):
		self.s = socket()
		self.s.connect(("172.22.27.191", 8001))
		self.s.send(packb({"type": "connect", "username": "YtvwlD"}))
		self.s.recv(10000)
		print ("Connected.")
		self.char = ""
	
	def move(self, direction, distance):
		self.s.send(packb({"type": "move", "direction": direction, "distance": distance}))
		print ("Moved: " + str((direction, distance)))
	
	def run(self):
		while True:
			self.whoami()
			self.get_Map()
			self.very_intelligent_artificial_intelligence()
			
	def get_Map(self):
		#print("Getting map...")
		self.s.send(packb({"type": "map"}))
		recv = b''
		while True:
			try:
				recv += self.s.recv(100000)
				answer = unpackb(recv)
				break
			except UnpackValueError:
				continue
		assert answer[0] == b"OK"
		#print ("Parsing the map...")
		self.map = Map(answer[1])
		#print ("Map parsed. ")
	
	def whoami(self):
		self.s.send(packb({"type": "whoami"}))
		answer = unpackb(self.s.recv(1000))
		assert answer[0] == b"OK"
		self.state = {"color": answer[1][0], "id": answer[1][1], "top": int(answer[1][2]/10), "left": int(answer[1][3]/10)}
		print ("whoami: " + str(self.state))
	
	def bomb(self, fuse_time):
		print("Achtung, Bombe! " + str(fuse_time))
		self.s.send(packb({"type": "bomb", "fuse_time": int(fuse_time)}))
		
	def very_intelligent_artificial_intelligence(self):
		"""Total intelligente künstliche Intelligenz!!!
		
		Na ja, sie geht in eine der vier Richtung, wenn das geht."""
		y = self.state["top"]
		x = self.state["left"]
		possibilities = list()
		def check(char, attr):
			if char == "a":
				new_x = x-1
				new_y = y
			elif char == "w":
				new_x = x
				new_y = y-1
			elif char == "d":
				new_x = x+1
				new_y = y
			elif char == "s":
				new_x = x
				new_y = y+1
			else:
				return False
			if new_x >= 0 and new_y >= 0 and new_x <= 48 and new_y <= 48: #nicht negativ und nicht über die Karte hinaus!
				print ("Block in " + char + " ist " + attr)
				return self.map[new_x][new_y].__getattribute__(attr)
			else: #da ist die Wand!!elf!
				return False
		while check(self.char, "moveable"):
			print("Can move: " + self.char)
			self.move(self.char, 1)
		for char in ("a", "w", "d", "s"):
			if check(char, "destructible"):
				self.bomb(5)
		for char in ("a", "w", "d", "s"): #a: left, w: up, d: right, s: down
			if check(char, "moveable"):
				#print("Moving possible: " + char)
				possibilities.append(char)
			#else:
			#	print("Moving not possible: " + char)
		if not possibilities:
			self.bomb(1)
		self.char = choice(possibilities)
		self.move(self.char, 1)
		#if choice([True, False, False, False]):
		#	self.bomb(1)
			
class Map(list):
	def __init__(self, string):
		list.__init__(self)
		y = 0
		string = string.decode("utf-8")
		for line in string.splitlines():
			dings = list()
			self.append(dings)
			x = 0
			for char in line:
				#if i == 1:
				char = str(char)
				print ("New block: " + char)
				dings.append(Block(char))
				x += 1
			y += 1
		#print ("Parsed the map.")

class Block():
	def __init__(self, char):
		self.moveable = char.islower()
		self.destructible = char == "W"
		#print ("New block! " + str({"moveable": self.moveable, "destructible": self.destructible}))

if __name__ == "__main__":
	bomber = Bomber()
	
	bomber.run()
	
	bomber.s.close()
