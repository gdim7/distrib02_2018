#!/usr/bin/env python

import socket
import select
import sys
import time
from chat_utils import *
import Queue
import signal

def signal_handler(signal, frame):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((TCP_IP, TCP_PORT))
	MESSAGE = 'ID: '+ usrid + ' !q'
	s.send(MESSAGE)
	print 'Disconnecting...'
	s.close()
	sys.exit()

signal.signal(signal.SIGINT, signal_handler)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

print 'Please provide your IP address, your preffered UDP port and username divided by a space'
MESSAGE = raw_input()
while (not len(MESSAGE.split(' ')) == 3):
	print 'Usage is: <IP_ADDR> <PORT> <USERNAME>'
	MESSAGE = raw_input()

UDP_IP = MESSAGE.split(' ')[0]
UDP_PORT = int(MESSAGE.split(' ')[1])
USERNAME = MESSAGE.split(' ')[2]
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind((UDP_IP, UDP_PORT))
s.send(MESSAGE)
data = s.recv(BUFFER_SIZE)
usrid = str(data.split(' ')[4])
print '[TRACKER]: ', data
s.close()

is_sequencer = {}
timestamps = {}
grp_timestamps = {}
stored_msgs = {}
grp_stored_msgs = {}
seq_addr = {}
seq_number = {}
stored_msgs_seq = []

def fifo_total_seq(msg):
	MESSAGE = msg.split('|')[0]
	current_grp = MESSAGE.split(' ')[1]
	id_timestamp = msg.split('|')[1]
	tid = id_timestamp.split(' ')[0]
	t = int(id_timestamp.split(' ')[1])
	if (tid == usrid):
		correct_t = grp_timestamps[current_grp][tid]
	else:
		correct_t = grp_timestamps[current_grp][tid] + 1
	if (correct_t == t):
		if (not tid == usrid):
			grp_timestamps[current_grp][tid] += 1
		for (ip, port) in seq_addr[current_grp]:
			udp_addr = (ip, int(port))
			msg = 'PRINT_MSG$$$' + MESSAGE + '$$$' + str(seq_number[current_grp])
			sent = udp_sock.sendto(msg, udp_addr)
		seq_number[current_grp] += 1	
		sys.stdout.write('\r')
		sys.stdout.flush()
		print MESSAGE
		correct_t += 1
		if (tid in grp_stored_msgs[current_grp]):
			flag = True	
			while(flag):
				flag = False
				for temp in grp_stored_msgs[current_grp][tid]:
					if (correct_t == int(temp.split('|')[0])):
						if (not tid == usrid):
							grp_timestamps[current_grp][tid] += 1
						correct_t += 1
						for (ip, port) in seq_addr[current_grp]:
							udp_addr = (ip, int(port))
							msg = 'PRINT_MSG$$$' + temp.split('|')[1] + '$$$' + str(seq_number[current_grp])
							sent = udp_sock.sendto(msg, udp_addr)
						seq_number[current_grp] += 1	
						sys.stdout.write('\r')
						sys.stdout.flush()
						print temp.split('|')[1]
						grp_stored_msgs[current_grp][tid].remove(temp)
						flag = True					
	elif (correct_t < t):
		for_store = str(t) + '|' + MESSAGE
		if not tid in stored_msgs:
			grp_stored_msgs[current_grp][tid] = []
			grp_stored_msgs[current_grp][tid].append(for_store)
		else:
			grp_stored_msgs[current_grp][tid].append(for_store)		
	else:
		sys.stdout.write('\r')
		sys.stdout.flush()			
		return
	return

def fifo_total(msg):
	MESSAGE = msg.split('$$$')[1]
	grp = MESSAGE.split(' ')[1]
	seq_no = int(msg.split('$$$')[2])
	if (seq_no == seq_number[grp]):
		seq_number[grp] += 1
		sys.stdout.write('\r')
		sys.stdout.flush()
		print MESSAGE
		if (len(stored_msgs_seq) > 0):
			flag = True	
			while(flag):
				flag = False
				for temp in stored_msgs_seq:
					if (seq_number[grp] == int(temp.split('|')[0])):
						seq_number[grp] += 1
						sys.stdout.write('\r')
						sys.stdout.flush()
						print temp.split('|')[1]
						stored_msgs_seq.remove(temp)
						flag = True					
	elif (seq_no > seq_number[grp]):
		for_store = str(seq_number[grp]) + '|' + MESSAGE
		stored_msgs_seq.append(for_store)		
	else:
		sys.stdout.write('\r')
		sys.stdout.flush()			
		return
	return


while 1:

	sys.stdout.write('[' + USERNAME + ']> ')
	sys.stdout.flush()

	sockets_list = [sys.stdin, udp_sock]
	outputs = []

	read_sockets, write_sockets, error_sockets = select.select(sockets_list, outputs, [])

	for socks in read_sockets:
		if socks == udp_sock:	
			MESSAGE, server = udp_sock.recvfrom(BUFFER_SIZE)
			if MESSAGE.startswith('REMOVE_USER'):
				removed_ip = MESSAGE.split(' ')[1]
				removed_port = MESSAGE.split(' ')[2]
				removed_id = MESSAGE.split(' ')[3]
				for key in grp_timestamps:
					for a in grp_timestamps[key]:
						if a==removed_id:
							del grp_timestamps[key][a]
							break
				for key in seq_addr:
					if is_sequencer[key]:
						for a in seq_addr[key]:
							if a==(removed_ip, removed_port):
								seq_addr[key].remove(a)
								break		
				for a in group_users:
					if a == (removed_ip, removed_port):
						group_users.remove((removed_ip, removed_port))
				sys.stdout.write('\r')
				sys.stdout.flush()
			elif MESSAGE.startswith('U_R_SEQUENCER'):
				if len(MESSAGE.split(' ')) == 2:
					seq_grp = MESSAGE.split(' ')[1]
					is_sequencer[seq_grp] = True
					seq_addr[grp] = []
					seq_number[seq_grp] = 0
				elif len(MESSAGE.split(' ')) == 4:
					if not grp in seq_addr:
						seq_addr[grp] = []
						seq_number[grp] = 0
						seq_grp = MESSAGE.split(' ')[1]
						for (ip, port) in group_users:
							udp_addr = (ip, int(port))
							sent = udp_sock.sendto('CURRENT_SEQ_NUMBER 0 ' + seq_grp, udp_addr)
					new_addr = (MESSAGE.split(' ')[2], MESSAGE.split(' ')[3])
					seq_addr[seq_grp].append(new_addr)
				elif len(MESSAGE.split(' ')) == 5:
					print 'mphke'
					print MESSAGE
					if not grp in seq_addr:
						seq_addr[grp] = []
						seq_number[grp] = 0
					seq_grp = MESSAGE.split(' ')[1]
					if is_sequencer[seq_grp]:
						for (ip, port) in group_users:
							udp_addr = (ip, int(port))
							sent = udp_sock.sendto('CURRENT_SEQ_NUMBER 0 ' + seq_grp, udp_addr)	
				sys.stdout.write('\r')
				sys.stdout.flush()		
			elif MESSAGE.startswith('MY_TIMESTAMP'):
				new_id = MESSAGE.split(' ')[1]
				new_grp = MESSAGE.split(' ')[3]
				grp_timestamps[new_grp][new_id] = int(MESSAGE.split(' ')[2])
				sys.stdout.write('\r')
				sys.stdout.flush()	
			elif MESSAGE.startswith('TIMESTAMP'):
				new_id = MESSAGE.split(' ')[1]
				new_grp = MESSAGE.split(' ')[4]
				grp_timestamps[new_grp][new_id] = 0
				udp_addr = (MESSAGE.split(' ')[2], int(MESSAGE.split(' ')[3]))
				tmstmp_msg = 'MY_TIMESTAMP ' + usrid + ' ' + str(grp_timestamps[new_grp][usrid]) + ' ' + new_grp
				sent = udp_sock.sendto(tmstmp_msg, udp_addr)
				sys.stdout.write('\r')
				sys.stdout.flush()
			elif MESSAGE.startswith('NEW_USER'):
				new_ip = MESSAGE.split(' ')[1]
				new_port = MESSAGE.split(' ')[2]
				new_id = MESSAGE.split(' ')[3]
				updated_grp = MESSAGE.split(' ')[8]
				if current_grp == updated_grp:
					group_users.append((new_ip, new_port))
				if is_sequencer[updated_grp]:
					udp_addr = (new_ip, int(new_port))
					sent = udp_sock.sendto('CURRENT_SEQ_NUMBER ' + str(seq_number[updated_grp]) + ' ' + updated_grp, udp_addr)
				sys.stdout.write('\r')
				sys.stdout.flush()
				print MESSAGE.split(':')[1]
			elif MESSAGE.startswith('CURRENT_SEQ_NUMBER'):
				seq_number[MESSAGE.split(' ')[2]] = int(MESSAGE.split(' ')[1])
				sys.stdout.write('\r')
				sys.stdout.flush()
			elif MESSAGE.startswith('PRINT_MSG'):
				fifo_total(MESSAGE)
			else:
				my_group = MESSAGE.split(' ')[1]
				if is_sequencer[my_group]:
					fifo_total_seq(MESSAGE)
				sys.stdout.write('\r')
				sys.stdout.flush()
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
				if (MESSAGE.split(' ')[2] == '!j'):
					grp = MESSAGE.split(' ')[3]
					if not grp in grp_timestamps:
						grp_timestamps[grp] = {}
						grp_timestamps[grp][usrid] = 0
						grp_stored_msgs[grp] = {}	
					if not grp in is_sequencer:
						is_sequencer[grp] = False	
				if (MESSAGE.split(' ')[2] == '!e' and current_grp == MESSAGE.split(' ')[3]):
					current_grp = None
				data = s.recv(BUFFER_SIZE)
				if (MESSAGE.split(' ')[2] == '!e' and data.startswith('You have been disconnected')):
					try:
						if is_sequencer[MESSAGE.split(' ')[3]]:
							is_sequencer[MESSAGE.split(' ')[3]] = False
							seq_addr[MESSAGE.split(' ')[3]] = []
						del grp_timestamps[MESSAGE.split(' ')[3]]	
					except:
						pass		
				if (MESSAGE.split(' ')[2] == '!w' and len(data.split(':')) == 2 and not data.startswith('Usage is:')):
					current_grp = MESSAGE.split(' ')[3]
					data = data.split(':')[1]
					users_info  = data.splitlines()
					group_users = []
					for strng in users_info:
						ip_port = strng.split(' ')
						group_users.append((ip_port[0], ip_port[1]))
				elif (MESSAGE.split(' ')[2] == '!j' and len(data.split(':')) == 2):
					is_sequencer[MESSAGE.split(' ')[3]] = True
				else:
					print '[TRACKER]: ', data
			else:
				if (not current_grp == None):
					grp_timestamps[current_grp][usrid] += 1
					for user in group_users:
						udp_addr = (user[0], int(user[1]))
						send_msg = ''
						send_msg = 'In ' + current_grp + ' ' + USERNAME + ' says:: ' + MESSAGE + '|' + usrid + ' ' + str(grp_timestamps[current_grp][usrid])
						sent = udp_sock.sendto(send_msg, udp_addr)
				else:
					print 'Please join a group in order to send messages.'