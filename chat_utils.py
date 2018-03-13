#!/usr/bin/env python

import threading
import os

TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024
GROUPS = {}
GROUPS_IDS = {}
USERS = {}
USER_READY_STR = 'Your user id is '
CMDERROR = 'Please enter a valid command.'
LMINPUTERROR = 'Usage is: !lm <group_name>'
JINPUTERROR = 'Usage is: !j <group_name>'
EINPUTERROR = 'Usage is: !e <group_name>'
WINPUTERROR = 'Usage is: !w <group_name>'
NOGROUPERROR = 'The group you have specified does not exist.'
NOUSERERROR = 'You are not member of the specified group.'
JMEMBERERROR = 'You are already member of the specified group.'
usrid = 0
MESSAGE = ''
group_users = []
current_grp = None
message_queue = {}


def ping_clients():
	threading.Timer(20.0, ping_clients).start()
	for user in USERS:
		hostname = USERS[user][0]
		response = os.system('ping -c 4 ' + hostname)
		if response == 0:
			print hostname, 'is up!'
		else:
			print hostname, 'is down!'
			"""for a in GROUPS.itervalues():
				try:
					a.remove(USERS[user][2])
				except ValueError:
					pass
			for a in GROUPS_IDS.itervalues():
				try:
					a.remove(user)
				except ValueError:
					pass"""
			MESSAGE = 'ID: ' + str(user) + ' !q'
			s.send(MESSAGE)
