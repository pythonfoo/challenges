#! /usr/bin/env python3
# coding: utf8

# bomber - eine total clevere KI für ein Bomberspiel
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
import asyncio
try:
	from msgpack.exceptions import OutOfData
except:
	pass #alte Version
from random import choice
from time import sleep
import sys

class Bomber:
	@asyncio.coroutine
	def connect(self):
		self.reader, self.writer = yield from asyncio.open_connection("172.22.27.221", 8001)
		self.writer.write(packb({"type": "connect", "username": "YtvwlD", "password": "", "async": True}))
		print ("Connected.")
		self.char = ""
		self.unpacker = Unpacker()
		self.bombed = False
		self.state = None
		self.moving = False
		self.waitforwhoami = False
		self.map = None
		asyncio.async(self.receiveandunpack())
		loop.call_soon(self.run)
	
	def move(self, direction, distance):
		if self.moving:
			return
		self.writer.write(packb({"type": "move", "direction": direction, "distance": distance}))
		if self.bombed:
				self.bombed += 1
		#answer = self.receive("ACK")
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
		self.moving = True
		self.waitforwhoami = True
		while self.state["left"] != new_x and self.state["top"] != new_y:
			while self.waitforwhoami:
				sleep(0.125)
		print ("Moved: " + str((direction, distance)) + " Distance to bomb: " + str(self.bombed))
		self.moving = False
	
	def run(self):
		self.writer.write(packb({"type": "whoami"}))
		self.writer.write(packb({"type": "map"}))
		self.writer.write(packb({"type": "what_bombs"}))
		if self.map and self.state:
			self.very_intelligent_artificial_intelligence()
		sleep(1)
		loop.call_soon(self.run)
	
	def parse(self, answer):
		if answer[0] == b"MAP":
			self.map = Map(answer[1])
		elif answer[0] == b"WHOAMI":
			self.state = {"color": answer[1][0], "id": answer[1][1], "top": int(int(answer[1][2])/10), "left": int(int(answer[1][3])/10)}
			print(answer[1][2])
			print(answer[1][3])
			print ("whoami: " + str(self.state))
			self.waitforwhoami = False
		elif answer[0] == b"BOMB":
			#for bomb in answer[1]:
				print("Neue Bombe gefunden: " + str(*answer[1:4]))
				self.map.add_bomb(*answer[1:4])
	
	@asyncio.coroutine
	def receiveandunpack(self):
		while not self.reader.at_eof():
			while True:
				try:
					recv = yield from self.reader.read(1024)
					self.unpacker.feed(recv)
					answer = self.unpacker.unpack()
					break
				except OutOfData:
					continue
			#print ("Received: " + str(answer))
			self.parse(answer)
			
		print ("Connection closed.")
		self.writer = None
	
	def bomb(self, fuse_time):
		print("Achtung, Bombe! " + str(fuse_time))
		self.bombed = 1
		self.writer.write(packb({"type": "bomb", "fuse_time": int(fuse_time)}))
		
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
		if check(self.char, "moveable"):
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
				print("Moving possible: " + char)
				possibilities.append(char)
			else:
				print("Moving not possible: " + char)
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
	
	def add_bomb(self, entry):
		self[entry[0][1]][entry[0][0]] = Bomb(*entry)

class Block():
	def __init__(self, char):
		self.char = char
		self.moveable = char.islower()
		self.destructible = char == "W"
		#print ("New block! " + str({"moveable": self.moveable, "destructible": self.destructible}))

class Bomb(Block):
	def __init__(self, update_timer, state, extra_info):
		Block.__init__(self, "B")
		#TODO

if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	bomber = Bomber()
	asyncio.async(bomber.connect())
	try:
		loop.run_forever()
	finally:
		loop.close()

#TODO: um die Ecke laufen
#TODO: gucken, wo Bomben sind

