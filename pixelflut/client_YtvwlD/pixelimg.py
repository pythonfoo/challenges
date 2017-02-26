#! /usr/bin/env python3

from __future__ import print_function

# pixelimg
# Copyright (C) 2017 Niklas Sombert
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

from sys import version_info, stdout, argv
from socket import socket
from PIL import Image
from random import randint
from multiprocessing import Process
from time import sleep

if version_info.major == 2:
	bp = print
	def print(text, end="\n", flush=False, *args, **kwargs):
		bp(text, end=end)
		if flush:
			stdout.flush()

def connect():
	print("(Re)Connecting...", end="")
	s = socket()
	s.connect((argv[1], int(argv[2])))
	s.send(b"OFFSET 750 250\n")
	return s

s = connect()
print("")
print("Opening image...")
image = Image.open(argv[3])
print("Querying size...", end="")
s.send(b"SIZE\n")
size = s.recv(100).decode().strip().split(" ")
#size = ["SIZE", 19999, 19999]
assert int(size[1]) < 20000
assert int(size[2]) < 20000
print(size)
print("Resizing...")
image = image.resize((int(int(size[1])/4), int(int(size[2])/4)))

class Th(Process):
	def __init__(self, image, *args, **kwargs):
		Process.__init__(self, *args, **kwargs)
		self.image = image.copy()

	def run(self):
		self.s = connect()
		print("Sending pixels...", end="", flush=True)
		count = 0
		for px in self.pixels():
			if not count % (2 * 8192):
				print(".", end="", flush=True)
				#print(px)
			self.send_pixel(**px)
			count += 1

	def send_pixel(self, x=0, y=0, px=None):
		#print(x, y, px)
		try:
			self.s.send("PX {} {} {:02x}{:02x}{:02x}\n".format(x, y, px[0], px[1], px[2]).encode())
			#print("PX {} {} {:02x}{:02x}{:02x}\n".format(x, y, px[0], px[1], px[2]).encode())
		except IOError:
			self.s = connect()
	def pixels(self):
		while True:
			x = randint(0, image.width-1)
			y = randint(0, image.height-1)
		#for x in range(image.width):
		#	for y in range(image.height):
			yield {"x": x, "y": y, "px": self.image.getpixel((x,y))}



print("Creating threads...", end="", flush=True)
threads = list()
for i in range(4):
	threads.append(Th(image))
	print(".", end="", flush=True)
print("")
print("Starting threads...")
for thread in threads:
	thread.start()
while True:
	try:
		sleep(5)
	except KeyboardInterrupt:
		print("Exiting...")
		for thread in threads:
			thread.terminate()
		exit()

