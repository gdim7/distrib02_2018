#!/usr/bin/env python

import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024
MESSAGE = ""

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
print "Please provide your IP address, your preffered UDP port and username divided by a space"
MESSAGE = raw_input()
s.send(MESSAGE)
data = s.recv(BUFFER_SIZE)
print "received data:", data
while 1:
	MESSAGE = raw_input()
	s.send(MESSAGE)
	data = s.recv(BUFFER_SIZE)
	print "received data:", data
s.close()

