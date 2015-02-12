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

class Hysgbakstryd:
	@asyncio.coroutine
	def connect(self):
		self.reader, self.writer = yield from asyncio.open_connection("172.22.27.40", 8001)
		self.writer.write(packb({"type": "connect", "username": "YtvwlD", "password": "", "async": True}))
		print ("Connected.")
		#...
		asyncio.async(self.receiveandunpack())
		loop.call_soon(self.run)
		
	def run(self):
		#...
		loop.call_soon(self.run)
	
	def parse(self, answer):
		pass
	
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

if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	hysgbakstryd = Hysgbakstryd()
	asyncio.async(hysgbakstryd.connect())
	try:
		loop.run_forever()
	finally:
		loop.close()
