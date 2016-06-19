#!/usr/bin/env python

from multiprocessing.dummy import Pool
from result import Result
from time import time
start_time = time()


def call_result(arg_tuple):
	return Result(*arg_tuple).dict

if __name__ == "__main__":
	ROll_NUM_LIST = range(170988,171088)
	pool = Pool(10)
	results = pool.map(call_result,((str(x),'SSC','2','2015') for x in ROll_NUM_LIST))
	pool.close()
	pool.join()
	print results

	print "========seconds=============" , time()-start_time
