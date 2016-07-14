#!/usr/bin/env python

import sqlite3

rollNumFile = open('rollNumFile.txt','r')
conn = sqlite3.connect('rollNumFile.sqlite')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS rollnums (
	rollnum INTEGER PRIMARY KEY,
	status INTEGER )''')
rollnums = [(int(x[0]),x[1]) for x in [eval(x) for x in rollNumFile.readlines()]]

for rollnum in rollnums:
	print "On rollnum" , rollnum
	try:
		c.execute('''INSERT INTO rollnums VALUES({rn},{st})'''.format(rn=rollnum[0],st=rollnum[1]))
	except sqlite3.IntegrityError:
		c.execute('''UPDATE rollnums SET status = {st} WHERE rollnum={rn}'''.format(rn=rollnum[0],st=rollnum[1]))
conn.commit()
