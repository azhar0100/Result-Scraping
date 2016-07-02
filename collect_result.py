#!/usr/bin/env python

from __future__ import print_function
from multiprocessing.dummy import Pool
from result import Result,StudentNotFound
from get_result import split_every
import sqlite3
import json
import logging
logger = logging.getLogger(__name__)
requests_logger = logging.getLogger('requests')
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
file_handler = logging.FileHandler("collect.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
requests_logger.addHandler(file_handler)

default_conf = {
	'DB_PATH' : "/home/azhar/db/rollNumFileCollected.sqlite",
	"DEGREE" : "SSC",
	"YEAR" : 2015,
	"PART" : 2
}

config = default_conf

conn = sqlite3.connect(config['DB_PATH'])
insert_conn = sqlite3.connect(config['DB_PATH'])
logger.info("Formed connection with the file : {}".format(config['DB_PATH']))
c = conn.cursor()
insert_c = insert_conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS result(
		rollnum INTEGER PRIMARY KEY,
		status INTEGER REFERENCES rolls(status),
		registration INTEGER,
		name TEXT,
		father_name TEXT,
		centre TEXT,
		date_of_birth DATE,
		marks TEXT)''')
current_rollNum = 0

while True:
	c.execute('''SELECT rollnum,status,html FROM rollnums WHERE status=1 and rollnum > {} limit 100'''.format(current_rollNum))
	chunk = c.fetchall()
	if chunk is None:
		break
	for rollnum,status,html in chunk:
		current_rollNum = rollnum
		rslt = Result(rollnum,*[str(config[x]) for x in ['DEGREE','PART','YEAR']],html=html)
		putlist = [getattr(rslt,x) for x in ['rollNum','regNum','student_name','father_name','centre','date_of_birth']]
		putlist.insert(1,status)
		putlist.append(json.dumps(rslt.marks_row))
		logger.info(putlist[0:-1])
		insert_c.execute('''INSERT INTO result VALUES(?,?,?,?,?,?,?,?)''',tuple(putlist))
	insert_conn.commit()
