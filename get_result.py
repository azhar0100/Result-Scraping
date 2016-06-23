#!/usr/bin/env python

from __future__ import print_function
from multiprocessing.dummy import Pool
from result import Result,StudentNotFound
from time import time
import re
import sqlite3
start_time = time()


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

if __name__ == "__main__":
	conn = sqlite3.connect('rollNumFile.sqlite')
	c = conn.cursor()
	avoid_rollNums = set([x[0] for x in c.execute(r'''SELECT rollnum FROM rollnums WHERE html!="" ''').fetchall()])
	print("Started building ROll_NUM_LIST")
	ROll_NUM_LIST = [x for x in range(100000,200000) if  x not in avoid_rollNums]
	print("Finished building ROll_NUM_LIST")
	POOL_SIZE = 12
	pool = Pool(POOL_SIZE)
	results = pool.imap(get_result,((str(x),'SSC','2','2015') for x in ROll_NUM_LIST))
	print('started')
	for result in results:
		try:
			c.execute(r'''INSERT INTO rollnums VALUES(?,?,?)''',(result[0],result[1],result[2]))
		except sqlite3.IntegrityError:
			c.execute(r'''UPDATE rollnums SET status = ?, html = ? WHERE rollnum=?''',(result[1],result[2],result[0]))
		conn.commit()
		print(result[0:2])
	pool.close()
	pool.join()

	print( "========seconds=============" , time()-start_time)
