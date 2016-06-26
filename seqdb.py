#!/usr/bin/env python
import sqlite3

conn = sqlite3.connect('rollNumFile.sqlite')
c = conn.cursor()

N = 2
rollNumSeqConn = sqlite3.connect('rtgz/rollNumFile{}00k.sqlite'.format(N))
rollNumSeqCurs = rollNumSeqConn.cursor()
rollNumSeqCurs.execute('''CREATE TABLE IF NOT EXISTS rollnums (
	rollnum INTEGER PRIMARY KEY,
	status INTEGER
	html TEXT )''')

rollnums = c.execute('''SELECT * FROM rollnums WHERE rollnum > 200000''').fetchall()
for rollnum in rollnums:
	rollNumSeqCurs.execute('''INSERT OR REPLACE INTO rollnums VALUES(?,?,?)''',rollnum[0],rollnum[1],rollnum[2])
