#!/usr/bin/env python

import sqlite3

rollNumFile = open('rollNumFi.txt','r')
conn = sqlite3.connect('rollNumFile.sqlite')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS rollnums (
	rollnum INTEGER PRIMARY KEY,
	status INTEGER )''')
rollnums = [(int(x[0]),x[1]) for x in [eval(x) for x in rollNumFile.readlines()]]

for rollnum in rollnums:
	print "On rollnum" , rollnum
	c.execute('''INSERT INTO rollnums VALUES({rn},{st})'''.format(rn=rollnum[0],st=rollnum[1]))

conn.commit()
