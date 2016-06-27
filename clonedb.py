#!/usr/bin/env python
import sqlite3
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(message)s',level=logging.DEBUG)

logger.info("Started the {} ".format(__name__))
conn = sqlite3.connect('rollNumFile.sqlite')
c = conn.cursor()
logger.info("Formed the database connection:{}".format(c))
N = 2
rollNumSeqConn = sqlite3.connect('rollNumFile-new.sqlite'.format(N))
rollNumSeqCurs = rollNumSeqConn.cursor()
logger.info("Formed the database connection:{}".format(rollNumSeqCurs))
rollNumSeqCurs.execute('''CREATE TABLE IF NOT EXISTS rollnums (
	rollnum INTEGER PRIMARY KEY,
	status INTEGER
	html TEXT )''')

rollnums = c.execute('''SELECT * FROM rollnums WHERE rollnum''')
count = 0
for rollnum in rollnums:
	count+=1
	logger.debug("Putting rollnum:{}".format(rollnum[0:2]))
	if not rollnum[2] == 0:
		rollNumSeqCurs.execute('''INSERT OR REPLACE INTO rollnums VALUES(?,?,?)''',(rollnum[0],rollnum[1],rollnum[2]))
	else:
		rollNumSeqCurs.execute('''INSERT OR REPLACE INTO rollnums VALUES(?,?,"")''',(rollnum[0],rollnum[1]))
	if count % 1000 == 0:
		logger.debug("Commit Now!")
		rollNumSeqConn.commit()
