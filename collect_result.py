#!/usr/bin/env python

from __future__ import print_function
from multiprocessing.dummy import Pool
from result import Result,StudentNotFound
import sqlite3
import json
import logging
logger = logging.getLogger(__name__)
requests_logger = logging.getLogger('requests')
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("collect.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
requests_logger.addHandler(file_handler)

def split_every(n, iterable):
    i = iter(iterable)
    piece = list(islice(i, n))
    while piece:
        yield piece
        piece = list(islice(i, n))

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
avoid_rollNums = set([x[0] for x in c.execute('''SELECT rollnum FROM result''')])
logger.info("Formed avoid_rollnums")
key_rollnums = [x for (x,) in c.execute('''SELECT rollnum FROM rolls WHERE status = 1''') if x not in avoid_rollNums]

count = 0
for key_rollnum in key_rollnums:
	count += 1
	(rollNum,status,html) = c.execute('''SELECT rollnum,status,html FROM rollnums WHERE rollnum = {}'''.format(key_rollnum)).fetchall()[0]
	rslt = Result(rollNum,*[str(config[x]) for x in ['DEGREE','PART','YEAR']],html=html)
	attr_list = ['rollNum','regNum','student_name','father_name','centre','date_of_birth']
	result_list = [getattr(rslt,x) for x in attr_list]
	result_list.insert(1,status)
	result_list.append(json.dumps(rslt.marks_row))
	logger.info(result_list[0:-1])
	c.execute('''INSERT INTO result VALUES(?,?,?,?,?,?,?,?)''',tuple(result_list))
	if count % 100:
		conn.commit()
