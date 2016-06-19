#!/usr/bin/env python

from multiprocessing.dummy import Pool
from result import Result
from time import time
# start_time = time()


def call_result(arg_tuple):
	return Result(*arg_tuple)
def get_dict(result_obj):
	return result_obj.dict

if __name__ == "__main__":
	ROll_NUM_LIST = xrange(170988,170998)
	pool = Pool(10)
	results = pool.map(call_result,((str(x),'SSC','2','2015') for x in ROll_NUM_LIST))
	pool.close()
	pool.join()
	print results


	pool = Pool(10)
	result_dicts = pool.map(get_dict,results)
	print result_dicts
	# print "========seconds=============" , time()-start_time
