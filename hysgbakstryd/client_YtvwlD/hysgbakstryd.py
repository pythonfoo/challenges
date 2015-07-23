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
from time import sleep
import asyncio
from zeroconf import Zeroconf
try:
	from msgpack.exceptions import OutOfData
except:
	pass #alte Version

class Hysgbakstryd:
	@asyncio.coroutine
	def connect(self):
		self.state = None
		self.reader, self.writer = yield from asyncio.open_connection("gimel", 8000)
		self.writer.write(packb({"type": "connect", "username": "YtvwlD", "password": "", "async": True}))
		print ("Connected.")
		self.writer.write(packb({"type": "activate"}))
		self.unpacker = Unpacker()
		#...
		asyncio.async(self.receiveandunpack())
		loop.call_soon(self.run)
		#self.move("up") #oder down oder halt
		self.writer.write(packb({"type": "shout", "foo": "bar"}))
		self.writer.write(packb({"type": "get_state"}))
		loop.call_later(5, lambda: self.go_to_level(8))
		loop.call_later(10, lambda: self.go_to_level(4))


	def run(self):
		if not self.state:
			loop.call_soon(self.run)
			return
		#...
		self.writer.write(packb({"type": "get_state"}))
		loop.call_later(2, self.run)
		#print ("Ready.")

	def parse(self, answer):
		command = answer[0].decode()
		username = answer[1].decode()
		content = answer[2]
		if command == "RESHOUT":
			print ("[SHOUT] {} said: {}".format(username, repr(content)))
		if command == "state":
			self.state = content

	def go_to_level(self, level):
		assert self.state is not None
		self.writer.write(packb({"type": "set_level", "level": level}))
		if level > self.state[b"level"]:
			direction = "up"
		elif level < self.state[b"level"]:
			direction = "down"
		else:
			print ("Well, nothing to do...")
		self.move(direction)

	def move(self, direction):
		self.writer.write(packb({"type": "set_direction", "direction": direction}))

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
			print ("Received: " + str(answer))
			#WARN: This produces bytestrings!
			self.parse(answer)

if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	hysgbakstryd = Hysgbakstryd()
	asyncio.async(hysgbakstryd.connect())
	try:
		loop.run_forever()
	finally:
		loop.close()
