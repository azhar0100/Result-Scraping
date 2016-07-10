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
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
file_handler = logging.FileHandler("collect.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)


def get_result_list(rollNum,degree,session,year,status,html):
	logger.debug("Called on rollNum:{}".format(rollNum))
	rslt = Result(rollNum,degree,session,year,html=html)
	attr_list = ['rollNum','regNum','student_name','father_name','centre','date_of_birth']
	result_list = [rslt.dict[x] for x in attr_list]
	result_list.insert(1,status)
	result_list.append(json.dumps(rslt.marks_row))
	logger.info(result_list[0:-1])
	return tuple(result_list)

def call_result_list(arg_tuple):
	return get_result_list(*arg_tuple)
def collect_result(
	dbpath=None,
	degree=None,
	session=None,
	year=None
	):

	conn = sqlite3.connect(dbpath)
	logger.info("Formed connection with the file : {}".format(dbpath))
	conn.execute('''CREATE TABLE IF NOT EXISTS result(
			rollnum INTEGER PRIMARY KEY,
			status INTEGER REFERENCES rolls(status),
			registration INTEGER,
			name TEXT,
			father_name TEXT,
			centre TEXT,
			date_of_birth DATE,
			marks TEXT)''')
	avoid_rollNums = set([x[0] for x in conn.execute('''SELECT rollnum FROM result''')])
	logger.info("Formed avoid_rollnums")
	key_rollnums = (x for (x,) in conn.execute('''SELECT rollnum FROM rolls WHERE status = 1''') if x not in avoid_rollNums)
	for chunk in split_every(100,key_rollnums):
		chunk_data = (conn.execute('''SELECT rollnum,status,html FROM rollnums WHERE rollnum = {}'''.format(x)).fetchone() for x in chunk)
		pool = Pool()
		result_chunk = pool.imap(call_result_list,[(x,)+(degree,session,year)+(y,z) for (x,y,z) in chunk_data])
		for reslt in result_chunk:
			if reslt[1]:
				conn.execute('''INSERT INTO result VALUES(?,?,?,?,?,?,?,?)''',reslt)
			elif reslt[1] == None:
				logger.critical("None Returned for args {}!".format(reslt[0][0:2]))
		logger.info("Commit Now!")
		conn.commit()
		logger.info("Joining the process Pool")
		pool.close()
		pool.join()
