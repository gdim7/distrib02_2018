#!/usr/bin/env python

import socket
import select
import sys
import time
from chat_utils import *

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

print 'Please provide your IP address, your preffered UDP port and username divided by a space'
MESSAGE = raw_input()
while (not len(MESSAGE.split(' ')) == 3):
	print 'Usage is: <IP_ADDR> <PORT> <USERNAME>'
	MESSAGE = raw_input()
s.send(MESSAGE)
data = s.recv(BUFFER_SIZE)
usrid = str(data.split(' ')[4])
print '[TRACKER]: ', data
s.close()

timestamps = {}
stored_msgs = {}

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
			if MESSAGE.startswith('REMOVE_USER'):
				removed_ip = MESSAGE.split(' ')[1]
				removed_port = MESSAGE.split(' ')[2]
				for a in group_users:
					if a == (removed_ip, removed_port):
						group_users.remove((removed_ip, removed_port))
				sys.stdout.write('\r')
				sys.stdout.flush()
			elif MESSAGE.startswith('NEW_USER'):
				new_ip = MESSAGE.split(' ')[1]
				new_port = MESSAGE.split(' ')[2]
				new_id = MESSAGE.split(' ')[3]
				updated_grp = MESSAGE.split(' ')[8]
				if current_grp == updated_grp:
					group_users.append((new_ip, new_port))
				sys.stdout.write('\r')
				sys.stdout.flush()
				print MESSAGE.split(':')[1]
			else:	
				sys.stdout.write('\r')
				sys.stdout.flush()
				print MESSAGE
		else:
			MESSAGE = raw_input()
			if (MESSAGE.startswith('!')):
				try:
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s.connect((TCP_IP, TCP_PORT))
				except:
					print 'You are already connected with id: ', usrid
				MESSAGE = 'ID: ' + usrid + ' ' + MESSAGE	
				s.send(MESSAGE)
				if (MESSAGE.split(' ')[2] == '!q'):
					print 'Disconnecting...'
					sys.exit()
				if (MESSAGE.split(' ')[2] == '!e' and current_grp == MESSAGE.split(' ')[3]):
					current_grp = None
				data = s.recv(BUFFER_SIZE)
				if (MESSAGE.split(' ')[2] == '!w' and len(data.split(':')) == 2):
					current_grp = MESSAGE.split(' ')[3]
					data = data.split(':')[1]
					users_info  = data.splitlines()
					group_users = []
					for strng in users_info:
						ip_port = strng.split(' ')
						group_users.append((ip_port[0], ip_port[1]))
				else:
					print '[TRACKER]: ', data
			else:
				if (not current_grp == None):
					for user in group_users:
						udp_addr = (user[0], int(user[1]))
						send_msg = ''
						send_msg = 'In ' + current_grp + ' ' + USERNAME + ' says:: ' + MESSAGE 
						sent = udp_sock.sendto(send_msg, udp_addr)
				else:
					print 'Please join a group in order to send messages.'