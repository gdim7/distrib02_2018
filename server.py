#!/usr/bin/env python

import socket
import select
import sys
import Queue


TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response
GROUPS = {}
USERS = {}
USER_READY_STR = 'Your user id is '
CMDERROR = 'Please enter a valid command.'
LMINPUTERROR = 'Usage is: !lm <group_name>'
JINPUTERROR = 'Usage is: !j <group_name>'
EINPUTERROR = 'Usage is: !e <group_name>'
NOGROUPERROR = 'The group you have specified does not exist.'
ENOUSERERROR = 'You are not member of the specified group.'
usrid = 0

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
				if (not data.startswith("ID: ")):
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
					grps = ''
					for key in GROUPS:
						grps += key + ' '
					message_queue[r].put(grps)
				
				elif (data.split(' ')[2] == '!lm'):
					input_length = len(data.split(' '))
					if (input_length == 4):
						grp = data.split(' ')[3]
						mbrs = ''
						try:
							for members in GROUPS[grp]:
								mbrs += members + ' '
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
						if not grp in GROUPS:
							GROUPS[grp] = []
							GROUPS[grp] = [USERS[tempid][2]]
						else:
							GROUPS[grp].append(USERS[tempid][2])	
						message_queue[r].put("You have been connected to the group " + grp)
					else:
						message_queue[r].put(JINPUTERROR)	
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
							if (flag):			
								message_queue[r].put("You have been disconnected from the group " + grp)
							else:
								message_queue[r].put(ENOUSERERROR)	
					else:
						message_queue[r].put(EINPUTERROR)
				else:
					message_queue[r].put(CMDERROR)
				print "received data:", data
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
