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

# def result_rollNum(arg_tuple):
# 	return jdump(call_result(arg_tuple).dict)

def result_rollNum(arg_tuple):
	try:
		return (call_result(arg_tuple).rollNum,1) 
	except Exception as e:
		return (arg_tuple[0],0)

if __name__ == "__main__":
	with open('rollNumFile.txt') as f:
		lines = f.readlines()
		avoid_rollNums = [int(eval(x)[0]) for x in lines]
	ROll_NUM_LIST = [x for x in range(170000,179999) if  x not in avoid_rollNums]
	POOL_SIZE = 12
	pool = Pool(POOL_SIZE)
	results = pool.imap(result_rollNum,((str(x),'SSC','2','2015') for x in ROll_NUM_LIST))
	# print results
	print('started')
	for result in results:
		# print('working')
		try:
			print(result,file=rollNumFile)
			print(result)
		except:
			break
	pool.close()
	pool.join()

	print( "========seconds=============" , time()-start_time)
