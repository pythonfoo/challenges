#!/usr/bin/env python3
from socket import socket
from sys import argv
from time import sleep

sockets = []
try:
	for i in range(1000):
		s = socket()
		s.connect(("10.42.1.89", 1234))
		sockets.append(s)
	while True:
		for s in sockets:
			s.send(b"HELP\n")
			s.recv(100)
		print(".", end="", flush=True)
		sleep(1)
finally:
	print(len(sockets))
