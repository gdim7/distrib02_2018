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
USER_READY_STR = 'A new user has now been created. Your user id is: '
usrid = 0
register = {}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setblocking(0)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

inputs = [s]
outputs = []

message_queue = {}

while inputs:
	readable, writeable, exceptional = select.select(inputs, outputs, inputs)
	print 'Sanity'
	for r in readable:
		if r is s:
			conn, addr = r.accept()
			conn.setblocking(0)
			inputs.append(conn)
			print 'Connection address:', addr
			message_queue[conn] = Queue.Queue()
			register[conn] = True
		else:
			data = r.recv(BUFFER_SIZE)
			if data:
				if (register[r] == True):
					register[r] == False
					ip = data.split(' ')[0]
					udp_port = data.split(' ')[1]
					username = data.split(' ')[2]
					USERS[usrid] = []
					USERS[usrid].append(ip)
					USERS[usrid].append(udp_port)
					USERS[usrid].append(username)
					message_queue[r].put(USER_READY_STR + str(usrid))
					usrid += 1
				elif (data == '!lg'):
					grps = ''
					for key in GROUPS:
						grps += key + ' '
					message_queue[r].put(grps)
				
				elif (data.startswith('!lm ')):
					grp = data.split(' ')[1]
					mbrs = ''
					try:
						for members in GROUPS[grp]:
							mbrs += members + ' '
					except:
						mbrs = 'There is no such group.'
					message_queue[r].put(mbrs)
				elif (data.startswith('!j ')):
					grp = data.split(' ')[1]
					mbrs = ''
					try:
						if not grp in GROUPS:
							GROUPS[grp] = []
							GROUPS[grp].append()
					except:
						mbrs = 'There is no such group.'
					message_queue[r].put(mbrs)
				else:
					message_queue[r].put(data)
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

	for e in exceptional:
		inputs.remove(e)
		if e in outputs:
			outputs.remove(e)
		e.close()
		del message_queue[e]
