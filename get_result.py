#!/usr/bin/env python

from multiprocessing.dummy import Pool
from result import Result
from time import time
start_time = time()


def call_result(arg_tuple):
	return Result(*arg_tuple)

if __name__ == "__main__":
	ROll_NUM_LIST = range(171188,171988)
	POOL_SIZE = 10
	pool = Pool(POOL_SIZE)
	results = pool.map(call_result,((str(x),'SSC','2','2015') for x in ROll_NUM_LIST))
	pool.close()
	pool.join()
	# print results
	print [x.rollNum for x in results].join('\n')

	print "========seconds=============" , time()-start_time
