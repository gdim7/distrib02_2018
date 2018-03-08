#!/usr/bin/env python

import socket
import select
import sys
import Queue
from chat_utils import *

#ping_clients()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setblocking(0)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

inputs = [s]
outputs = []

message_queue = {}

while inputs:
	readable, writeable, exceptional = select.select(inputs, outputs, inputs)
	for r in readable:
		if r is s:
			conn, addr = r.accept()
			conn.setblocking(0)
			inputs.append(conn)
			print 'Connection address:', addr
			message_queue[conn] = Queue.Queue()
		else:
			data = r.recv(BUFFER_SIZE)
			if data:
				if (not data.startswith('ID: ')):
					ip = data.split(' ')[0]
					udp_port = data.split(' ')[1]
					username = data.split(' ')[2]
					tempid = str(usrid)
					USERS[tempid] = []
					USERS[tempid].append(ip)
					USERS[tempid].append(udp_port)
					USERS[tempid].append(username)
					for value in USERS[tempid]:
						print value
					message_queue[r].put(USER_READY_STR + tempid)
					usrid += 1
				elif (data.split(' ')[2] == '!lg'):
					grps = 'groups: '
					for key in GROUPS:
						grps += '[' + key + '] '
					message_queue[r].put(grps)
				
				elif (data.split(' ')[2] == '!lm'):
					input_length = len(data.split(' '))
					if (input_length == 4):
						grp = data.split(' ')[3]
						mbrs = 'members: '
						try:
							for members in GROUPS[grp]:
								mbrs += '(' + members + ') '
						except:
							mbrs = NOGROUPERROR
						message_queue[r].put(mbrs)
					else:
						message_queue[r].put(LMINPUTERROR)	
				elif (data.split(' ')[2] == '!j'):
					input_length = len(data.split(' '))
					if (input_length == 4):
						tempid = data.split(' ')[1]
						grp = data.split(' ')[3]
						if not tempid in USERS:
							USERS
						if not grp in GROUPS:
							GROUPS[grp] = []
							GROUPS[grp] = [USERS[tempid][2]]
							GROUPS_IDS[grp]= [tempid]
							message_queue[r].put('You have been connected to the group ' + grp)
						else:
							if not tempid in GROUPS_IDS[grp]:
								GROUPS[grp].append(USERS[tempid][2])
								GROUPS_IDS[grp].append(tempid)	
								new_udp_ip = USERS[tempid][0]
								new_udp_port = USERS[tempid][1]
								new_username = USERS[tempid][2]
								update_msg =  'NEW_USER ' + new_udp_ip + ' ' + new_udp_port + ' ' + tempid + ' :' + new_username + ' has now joined ' + grp
								udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
								for user in GROUPS_IDS[grp]:
									if not user == tempid:
										udp_addr = (USERS[user][0], int(USERS[user][1]))
										sent = udp_socket.sendto(update_msg, udp_addr)
								message_queue[r].put('You have been connected to the group ' + grp)
							else:
								message_queue[r].put(JMEMBERERROR)
					else:
						message_queue[r].put(JINPUTERROR)
				elif (data.split(' ')[2] == '!q'):
					tempid = data.split(' ')[1]
					for a in GROUPS.itervalues():
						try:
							a.remove(USERS[tempid][2])
						except ValueError:
							pass
					for a in GROUPS_IDS.itervalues():
						try:
							a.remove(tempid)
						except ValueError:
							pass
					remove_ip = USERS[tempid][0]
					remove_port = USERS[tempid][1]
					remove_msg = 'REMOVE_USER ' + remove_ip + ' ' + remove_port
					udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
					for user in USERS:
						#if not user == tempid:
						udp_addr = (USERS[user][0], int(USERS[user][1]))
						sent = udp_socket.sendto(remove_msg, udp_addr)
				elif (data.split(' ')[2] == '!w'):
					input_length = len(data.split(' '))
					if (input_length == 4):
						tempid = data.split(' ')[1]
						grp = data.split(' ')[3]
						if not grp in GROUPS:
							message_queue[r].put(NOGROUPERROR)
						elif not tempid in GROUPS_IDS[grp]:
							message_queue[r].put(NOUSERERROR)
						else:
							ips_ports  =  'answer:'
							for temp_i in GROUPS_IDS[grp]:
								ips_ports += USERS[temp_i][0] +  ' ' + USERS[temp_i][1] + '\n'
							message_queue[r].put(ips_ports)
					else:
						message_queue[r].put(WINPUTERROR)	
				elif (data.split(' ')[2] == '!e'):
					input_length = len(data.split(' '))
					if (input_length == 4):
						tempid = data.split(' ')[1]
						grp = data.split(' ')[3]
						if not grp in GROUPS:
							message_queue[r].put(NOGROUPERROR)
						else:
							flag = False
							for a in GROUPS.itervalues():
								try:
									a.remove(USERS[tempid][2])
									flag = True
								except ValueError:
									pass
							for a in GROUPS_IDS.itervalues():
								try:
									a.remove(tempid)
								except ValueError:
									pass
							
							if (flag):			
								message_queue[r].put('You have been disconnected from the group ' + grp)
								remove_ip = USERS[tempid][0]
								remove_port = USERS[tempid][1]
								remove_msg = 'REMOVE_USER ' + remove_ip + ' ' + remove_port
								udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
								for user in GROUPS_IDS[grp]:
									#if not user == tempid:
									udp_addr = (USERS[user][0], int(USERS[user][1]))
									sent = udp_socket.sendto(remove_msg, udp_addr)
							else:
								message_queue[r].put(NOUSERERROR)	
					else:
						message_queue[r].put(EINPUTERROR)
				else:
					message_queue[r].put(CMDERROR)
				print 'received data:', data
				if r not in outputs:
					outputs.append(r)
			else:
				if r in outputs:
					outputs.remove(r)
				inputs.remove(r)
				r.close()
				del message_queue[r]

	for w in writeable:
		try:
			msg = message_queue[w].get_nowait()
		except Queue.Empty:
			outputs.remove(w)
		else:
			w.send(msg)
			inputs.remove(w)
			if w in outputs:
				outputs.remove(w)
			w.close()
			del message_queue[w]
	for e in exceptional:
		inputs.remove(e)
		if e in outputs:
			outputs.remove(e)
		e.close()
		del message_queue[e]