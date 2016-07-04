#!/usr/bin/env python

from __future__ import print_function
from multiprocessing import Pool
from result import Result,StudentNotFound
from lib import split_every
from itertools import imap
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

conf_path = 'collect.json'
logger.info("Reading conf from: {}".format(conf_path))
try:
	with open(conf_path,'r') as f:
		file_config = json.loads(f.read())
except IOError:
	file_config = {}
logger.info("Read config as {}".format(file_config))
config = {}
config.update(file_config)

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

def get_result_list(rollNum,status,html):
	rslt = Result(rollNum,*[str(config[x]) for x in ['DEGREE','PART','YEAR']],html=html)
	attr_list = ['rollNum','regNum','student_name','father_name','centre','date_of_birth']
	result_list = [getattr(rslt,x) for x in attr_list]
	result_list.insert(1,status)
	result_list.append(json.dumps(rslt.marks_row))
	logger.info(result_list[0:-1])
	return tuple(result_list)

def call_result_list(arg_tuple):
	return get_result_list(*arg_tuple)
if __name__ == '__main__':
	for chunk in split_every(100,key_rollnums):
		chunk_data = [c.execute('''SELECT rollnum,status,html FROM rollnums WHERE rollnum = {}'''.format(x)).fetchone() for x in chunk]
		pool = Pool()
		result_chunk = pool.imap(call_result_list,chunk_data)
		for reslt in result_chunk:
			c.execute('''INSERT INTO result VALUES(?,?,?,?,?,?,?,?)''',reslt)
		logger.info("Commit Now!")
		conn.commit()
		logger.info("Joining the process Pool")
		pool.close()
		pool.join()
