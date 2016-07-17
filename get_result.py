#!/usr/bin/env python

from __future__ import print_function
from multiprocessing.dummy import Pool
from result import Result,StudentNotFound
from time import time
from itertools import islice
from lib import lazy_imap
import re
import sqlite3
import json
import logging
import atexit
start_time = time()

logger = logging.getLogger('get_result')
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.addFilter(logging.Filter("get_result"))
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

def call_result(arg_tuple):
	return Result(*arg_tuple)

def get_result_html(arg_tuple):
	try:
		html = call_result(arg_tuple).html
		return arg_tuple + (1,html) 
	except StudentNotFound as e:
		return (arg_tuple) + (0,'')
	except IOError as e:
		return (arg_tuple) + (2,'')
	except Exception as e:
		return (arg_tuple) + (3,'')

def deep_query(cursor):
	return cursor.execute(r'''SELECT rollnum FROM rollnums WHERE html!="" OR status=0 ''').fetchall()

def shallow_query(cursor):
	return cursor.execute(r'''SELECT rollnum FROM rolls 
		WHERE status=1 
		AND (status=0 AND degree = ? AND session = ?)''',(degree,session)).fetchall()

def get_result(dbpath=None,
	degree=['SSC','HSSC'],
	session=range(3),
	year=None,
	request_chunk_size=1000,
	database_chunk_size=100,
	pool_size=100,
	log_dir='.'):

	degree_ints = {'SSC':1,'HSSC':2}
	
	file_handler = logging.FileHandler("{}/get_result.log".format(log_dir))
	file_handler.setLevel(logging.DEBUG)
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)

	logger.info("Trying to form connection to file:{}".format(dbpath))
	conn = sqlite3.connect(dbpath)
	logger.info("Formed connection with the file:{}".format(dbpath))

	atexit.register(lambda x: x.commit() , conn)
	conn.execute('''CREATE TABLE IF NOT EXISTS rollStatus(
		rollnum INTEGER,
		degree INTEGER,
		session INTEGER,
		status INTEGER,
		FOREIGN KEY(degree) REFERENCES degrees(id),
		PRIMARY KEY(rollnum,degree,session)
		);
	''')
	conn.execute('''CREATE TABLE IF NOT EXISTS resultHtml(
		rollnum INTEGER PRIMARY KEY,
		html TEXT
		)''')

	for current_degree in degree:
		for current_session in session:
			avoid_rollNums = set([x for (x,) in conn.execute(r'''SELECT rollnum FROM rollStatus WHERE status=1 OR (status=0 AND degree = ? AND session = ?)''',(current_degree,current_session))])
			logger.info("Formed the avoid_rollNums set")
			ROLL_NUM_LIST = [(x,current_degree,current_session,year) for x in (x for x in range(000000,999999) if  x not in avoid_rollNums)]
			logger.info("Formed the ROLL_NUM_LIST")
			start_time = time()
			pool = Pool(pool_size)
			results = lazy_imap(get_result_html,ROLL_NUM_LIST,pool,request_chunk_size)
			count = 0
			for result in results:
				count += 1
				conn.execute(r'''INSERT OR REPLACE INTO rollStatus VALUES(?,?,?,?)''',result[0:3] + (result[4],))
				if result[1] == 1:
					conn.execute(r'''INSERT OR REPLACE INTO resultHtml VALUES(?,?)''',tuple((result[x] for x in [0,-1])))
				if result[1] == 2:
					ROLL_NUM_LIST.append(result[0],current_degree,current_session,year)
				if count % database_chunk_size == 0:
					logger.info("Commit Now at {}".format(count))
					conn.commit()
				logger.info(result[0:-1])
			logger.info("End Commit at {}".format(count))
			conn.commit()
			logger.info( "========seconds============={}".format(time()-start_time))
			pool.close()
			pool.join()

