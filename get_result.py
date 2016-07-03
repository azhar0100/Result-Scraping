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
start_time = time()
logger = logging.getLogger('get_result')
requests_logger = logging.getLogger('requests')
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.addFilter(logging.Filter("get_result"))
file_handler = logging.FileHandler("rollNumFile.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
requests_logger.addHandler(file_handler)
conf_path = 'get_result.json'
logger.info("Reading conf from{}".format(conf_path))
try:
	with open(conf_path,'r') as f:
		file_config = json.loads(f.read())
except IOError:
	file_config = {}
logger.info("Read config as {}".format(file_config))
config = {}
config.update(file_config)

def call_result(arg_tuple):
	return Result(*arg_tuple)

def get_result(arg_tuple):
	try:
		rslt = call_result(arg_tuple)
		return (rslt.rollNum,1,rslt.html) 
	except StudentNotFound as e:
		return (arg_tuple[0],0,'')
	except IOError as e:
		return (arg_tuple[0],2,'')
	except Exception as e:
		return (arg_tuple[0],3,'')

def deep_query(cursor):
	return cursor.execute(r'''SELECT rollnum FROM rollnums WHERE html!="" OR status=0 ''').fetchall()

def shallow_query(cursor):
	return cursor.execute(r'''SELECT rollnum FROM rolls WHERE status=0 OR status=1''').fetchall()

if __name__ == "__main__":
	conn = sqlite3.connect(config['DB_PATH'])
	logger.info("Formed connection with the file:{}".format(config['DB_PATH']))
	c = conn.cursor()
	avoid_rollNums = set([x[0] for x in shallow_query(c)])
	logger.info("Formed the avoid_rollNums set")
	ROLL_NUM_LIST = [x for x in range(000000,999999) if  x not in avoid_rollNums]
	logger.info("Formed the ROLL_NUM_LIST")
	ROLL_NUM_TUPLE_LIST= [(str(x).zfill(6),config['DEGREE'],str(config['PART']),str(config['YEAR'])) for x in ROLL_NUM_LIST]
	start_time = time()
	pool = Pool(config['POOL_SIZE'])
	results = lazy_imap(get_result,ROLL_NUM_TUPLE_LIST,pool,config['REQUEST_CHUNK_SIZE'])
	count = 0
	for result in results:
		count += 1
		c.execute(r'''INSERT OR REPLACE INTO rollnums VALUES(?,?,?)''',result)
		c.execute(r'''INSERT OR REPLACE INTO rolls VALUES(?,?)''',result[0:2])
		if result[1] == 2:
			ROLL_NUM_TUPLE_LIST.append((str(result[0]),'SSC','2','2015'))
		if count % config['DATABASE_CHUNK_SIZE'] == 0:
			logger.info("Commit Now at {}".format(count))
			conn.commit()
		logger.info(result[0:2])
	logger.info("End Commit at {}".format(count))
	conn.commit()
	logger.info( "========seconds============={}".format(time()-start_time))
	pool.close()
	pool.join()

