#!/usr/bin/env python

import socket
import select
import sys
import time


TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024
MESSAGE = ""
group_users = []
grp = None

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

print "Please provide your IP address, your preffered UDP port and username divided by a space"
MESSAGE = raw_input()
while (not len(MESSAGE.split(' ')) == 3):
	print 'Usage is: <IP_ADDR> <PORT> <USERNAME>'
	MESSAGE = raw_input()
s.send(MESSAGE)
data = s.recv(BUFFER_SIZE)
usrid = str(data.split(' ')[4])
print '[TRACKER]: ', data
s.close()

UDP_IP = MESSAGE.split(' ')[0]
UDP_PORT = int(MESSAGE.split(' ')[1])
USERNAME = MESSAGE.split(' ')[2]

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind((UDP_IP, UDP_PORT))

while 1:

	sys.stdout.write('[' + USERNAME + ']> ')
	sys.stdout.flush()

	sockets_list = [sys.stdin, udp_sock]

	read_sockets, write_sockets, error_sockets = select.select(sockets_list, [], [])

	for socks in read_sockets:
		if socks == udp_sock:
			MESSAGE, server = udp_sock.recvfrom(BUFFER_SIZE)
			sys.stdout.write('\r')
			sys.stdout.flush()
			print (MESSAGE)
		else:
			MESSAGE = raw_input()
			if (MESSAGE.startswith('!')):
				try:
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s.connect((TCP_IP, TCP_PORT))
				except:
					print "You are already connected with id: ", usrid
				MESSAGE = "ID: " + usrid + " " + MESSAGE	
				s.send(MESSAGE)
				if (MESSAGE.split(' ')[2] == '!q'):
					print 'Disconnecting...'
					sys.exit()
				if (MESSAGE.startswith('!e') and grp == MESSAGE.split(' ')[3]):
					grp = None
				data = s.recv(BUFFER_SIZE)
				if (MESSAGE.split(' ')[2] == '!w' and len(data.split(':')) == 2):
					grp = MESSAGE.split(' ')[3]
				else:
					print '[TRACKER]: ', data
			else:

				if (not grp == None):
					try:
						s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						s.connect((TCP_IP, TCP_PORT))
					except:
						print 'You are already connected with id: ', usrid	
					msg = 'ID: ' + usrid + ' ' + '!w ' + grp	
					s.send(msg)
					data = s.recv(1024)
					data = data.split(':')[1]
					users_info  = data.splitlines()
					group_users = []
					for strng in users_info:
						ip_port = strng.split(' ')
						group_users.append((ip_port[0], ip_port[1]))
					for user in group_users:
						udp_addr = (user[0], int(user[1]))
						send_msg = ''
						send_msg = 'In ' + grp + ' ' + USERNAME + ' says:: ' + MESSAGE 
						sent = udp_sock.sendto(send_msg, udp_addr)
				else:
					print 'Please join a group in order to send messages.'