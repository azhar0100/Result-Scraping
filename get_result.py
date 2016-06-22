#!/usr/bin/env python

from __future__ import print_function
from multiprocessing.dummy import Pool
from result import Result,StudentNotFound
from time import time
from json import dumps as jdump
import re
import sqlite3
start_time = time()


def call_result(arg_tuple):
	return Result(*arg_tuple)

def result_rollNum(arg_tuple):
	try:
		return (call_result(arg_tuple).rollNum,1) 
	except StudentNotFound as e:
		return (arg_tuple[0],0)
	except IOError as e:
		return (arg_tuple[0],2)
	except Exception as e:
		return (arg_tuple[0],3)

if __name__ == "__main__":
	conn = sqlite3.connect('rollNumFile.sqlite')
	c = conn.cursor()
	avoid_rollNums = set([x[0] for x in c.execute(r'''SELECT rollnum FROM rollnums WHERE status = 1 OR status = 0 OR html='' ''').fetchall()])
	print("Started building ROll_NUM_LIST")
	ROll_NUM_LIST = [x for x in range(100000,200000) if  x not in avoid_rollNums]
	print("Finished building ROll_NUM_LIST")
	POOL_SIZE = 12
	pool = Pool(POOL_SIZE)
	results = pool.imap(result_rollNum,((str(x),'SSC','2','2015') for x in ROll_NUM_LIST))
	print('started')
	for result in results:
		try:
			c.execute('''INSERT INTO rollnums VALUES({rn},{st})'''.format(rn=result[0],st=result[1]))
		except sqlite3.IntegrityError:
			c.execute('''UPDATE rollnums SET status = {st} WHERE rollnum={rn}'''.format(rn=result[0],st=result[1]))
		conn.commit()
		print(result)
	pool.close()
	pool.join()

	print( "========seconds=============" , time()-start_time)
