#!/usr/bin/env python

from __future__ import print_function
from multiprocessing.dummy import Pool
from result import Result,StudentNotFound
from time import time
from itertools import islice
import re
import sqlite3
start_time = time()

def split_every(n, iterable):
    i = iter(iterable)
    piece = list(islice(i, n))
    while piece:
        yield piece
        piece = list(islice(i, n))

def lazy_imap(func,arglist,pool,chunksize=1):
	for chunk in split_every(chunksize,arglist):
		chunk_results = pool.imap_unordered(func,chunk)
		for chunk_result in chunk_results:
			yield chunk_result

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
	# avoid_rollNums = set([x[0] for x in c.execute(r'''SELECT rollnum FROM rollnums WHERE html!="" ''').fetchall()])
	avoid_rollNums=[]
	print("Started building ROll_NUM_LIST")
	ROll_NUM_LIST = [x for x in range(200199,200300) if  x not in avoid_rollNums]
	print("Finished building ROll_NUM_LIST")
	start_time = time()
	POOL_SIZE = 100
	pool = Pool(POOL_SIZE)
	results = lazy_imap(get_result,[(str(x),'SSC','2','2015') for x in ROll_NUM_LIST],pool,100)
	print('started')
	for result in results:
		try:
			c.execute(r'''INSERT INTO rollnums VALUES(?,?,?)''',(result[0],result[1],result[2]))
		except sqlite3.IntegrityError:
			c.execute(r'''UPDATE rollnums SET status = ?, html = ? WHERE rollnum=?''',(result[1],result[2],result[0]))
		conn.commit()
		print(result[0:2])
	print( "========seconds=============" , time()-start_time)
	pool.close()
	pool.join()

