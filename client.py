#!/usr/bin/env python

import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024
MESSAGE = ""
group_users = []

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
print "Please provide your IP address, your preffered UDP port and username divided by a space"
MESSAGE = raw_input()
s.send(MESSAGE)
data = s.recv(BUFFER_SIZE)
usrid = str(data.split(' ')[4])
print "received data:", data
s.close()
while 1:
	MESSAGE = raw_input()
	if (MESSAGE.startswith('!')):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((TCP_IP, TCP_PORT))
		except:
			print "You are already connected with id: ", usrid		
		MESSAGE = "ID: " + usrid + " " + MESSAGE	
		s.send(MESSAGE)
		data = s.recv(BUFFER_SIZE)
		if (MESSAGE.split(' ')[2] == '!w' and len(data.split(':')) == 2):
			data = data.split(':')[1]
			users_info  = data.splitlines()
			group_users = []
			for strng in users_info:
				ip_port = strng.split(' ')
				group_users.append((ip_port[0], ip_port[1]))
			print group_users
		print "received data:", data
	else:
		print "Enter a valid command."