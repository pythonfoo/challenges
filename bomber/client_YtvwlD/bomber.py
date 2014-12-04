#! /usr/bin/env python3
# coding: utf8

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
from msgpack import packb, Unpacker
try:
	from msgpack.exceptions import OutOfData
except:
	pass #alte Version
from random import choice
from time import sleep
import sys

class Bomber:
	def __init__(self):
		self.s = socket()
		self.s.connect(("172.22.27.191", 8001))
		self.s.send(packb({"type": "connect", "username": "YtvwlD", "password": ""}))
		self.s.recv(10000)
		print ("Connected.")
		self.char = ""
		self.unpacker = Unpacker()
		self.bombed = False
	
	def move(self, direction, distance):
		self.s.send(packb({"type": "move", "direction": direction, "distance": distance}))
		if self.bombed:
				self.bombed += 1
		answer = self.receiveandunpack()
		if not answer[0] == b"ACK":
			return
		x,y = self.state["left"], self.state["top"]
		if direction == "a":
			new_x = x-1
			new_y = y
		elif direction == "w":
			new_x = x
			new_y = y-1
		elif direction == "d":
			new_x = x+1
			new_y = y
		elif direction == "s":
			new_x = x
			new_y = y+1
		else:
			return False
		while self.state["left"] != new_x and self.state["top"] != new_y:
			sleep(0.125)
			self.whoami()
		print ("Moved: " + str((direction, distance)) + " Distance to bomb: " + str(self.bombed))
	
	def run(self):
		while True:
			self.whoami()
			self.get_Map()
			self.very_intelligent_artificial_intelligence()
			
	def get_Map(self):
		#print("Getting map...")
		self.s.send(packb({"type": "map"}))
		answer = self.receiveandunpack()
		if not answer[0] == b"MAP":
			return
		#print ("Parsing the map...")
		self.map = Map(answer[1])
		#print ("Map parsed. ")
	
	def receiveandunpack(self):
		while True:
			try:
				recv = self.s.recv(100000)
				self.unpacker.feed(recv)
				answer = self.unpacker.unpack()
				break
			except OutOfData:
				continue
		return answer
	
	def whoami(self):
		self.s.send(packb({"type": "whoami"}))
		answer = self.receiveandunpack()
		if not answer[0] == b"WHOAMI":
			return
		self.state = {"color": answer[1][0], "id": answer[1][1], "top": int(answer[1][2]/10), "left": int(answer[1][3]/10)}
		print ("whoami: " + str(self.state))
	
	def bomb(self, fuse_time):
		print("Achtung, Bombe! " + str(fuse_time))
		self.bombed = 1
		self.s.send(packb({"type": "bomb", "fuse_time": int(fuse_time)}))
		self.s.recv(10000)
		
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
				result = self.map[new_y][new_x].__getattribute__(attr)
				#print ("Block in {} (x: {}, y: {}, char: {}) ist {}: {}".format(char, new_x, new_y, self.map[new_x][new_y].char, attr, str(result)))
				return result
			else: #da ist die Wand!!elf!
				return False
		while check(self.char, "moveable"):
			self.move(self.char, 1)
			return
		print (self.bombed)
		if self.bombed > 11:
			print ("Warte in einer sicheren Ecke auf die Explosion der Bombe...")
			sleep(5)
		else:
			print ("Ich vielleicht werde sterben!")
		self.bombed = 0
		bomb = False
		for char in ("a", "w", "d", "s"):
			if check(char, "destructible"):
				bomb = True
		if bomb:
			self.bomb(5)
		for char in ("a", "w", "d", "s"): #a: left, w: up, d: right, s: down
			if check(char, "moveable"):
				#print("Moving possible: " + char)
				possibilities.append(char)
			#else:
			#	print("Moving not possible: " + char)
		if not possibilities:
			self.bomb(1)
			self.char = ""
			return
		#self.map.print()
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
				#print ("New block: " + char)
				dings.append(Block(char))
				x += 1
			y += 1
		#print ("Parsed the map.")
	
	def print(self):
		for line in self:
			for block in line:
				sys.stdout.write(block.char)
			sys.stdout.write("\n")

class Block():
	def __init__(self, char):
		self.char = char
		self.moveable = char.islower()
		self.destructible = char == "W"
		#print ("New block! " + str({"moveable": self.moveable, "destructible": self.destructible}))

if __name__ == "__main__":
	bomber = Bomber()
	
	bomber.run()
	
	bomber.s.close()
