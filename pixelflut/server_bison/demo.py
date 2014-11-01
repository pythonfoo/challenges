# Echo server program
import socket
import sys
import json
HOST = None			   # Symbolic name meaning all available interfaces
PORT = 9999			  # Arbitrary non-privileged port
s = None
for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
							  socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
	af, socktype, proto, canonname, sa = res
	try:
		s = socket.socket(af, socktype, proto)
	except socket.error as msg:
		s = None
		continue
	try:
		s.bind(sa)
		s.listen(1)
	except socket.error as msg:
		s.close()
		s = None
		continue
	break
if s is None:
	print 'could not open socket'
	sys.exit(1)

while 1:
	try:

		conn, addr = s.accept()
		print 'Connected by', addr
		try:
			jsonString = ''
			while 1:
				data = conn.recv(2048)
				print 'data"', data, '"'
				hasEx = False
				if not data:
					break
				try:
					jsonString = json.loads(data)
				except Exception as ex:
					print 'json error', ex
					conn.sendall('json error')
					hasEx = True

				if hasEx == False:
					if not 'user' in jsonString:
						conn.sendall('NO USER!')
					elif  not 'x' in jsonString or not 'y' in jsonString:
						conn.sendall('NO X OR Y!')
					elif  not 'color' in jsonString:
						conn.sendall('color error')
				else:
					conn.sendall('ok')

				conn.sendall('ok')
		finally:
			if conn != None:
				try:
					conn.close()
				except Exception as ex:
					print ex
	except Exception as ex:
		print ex
