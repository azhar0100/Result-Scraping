#!/usr/bin/env python

from __future__ import print_function
from multiprocessing.dummy import Pool
from result import Result
from time import time
from json import dumps as jdump
start_time = time()


def call_result(arg_tuple):
	try:
		return Result(*arg_tuple)
	except Exception as e:
		return e

def result_rollNum(arg_tuple):
	return jdump(call_result(arg_tuple).dict)

# def result_rollNum(arg_tuple):
	# return call_result(arg_tuple).params[0]

if __name__ == "__main__":
	ROll_NUM_LIST = range(171384,171393)
	POOL_SIZE = 10
	pool = Pool(POOL_SIZE)
	results = pool.imap(result_rollNum,((str(x),'SSC','2','2015') for x in ROll_NUM_LIST))
	# print results
	print('started')
	rollNumFile = open("rollNumFile.txt",'w')
	for result in results:
		print('working')
		try:
			print(result,file=rollNumFile)
		except:
			break
	pool.close()
	pool.join()

	print( "========seconds=============" , time()-start_time)
