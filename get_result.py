#!/usr/bin/env python

from multiprocessing.dummy import Pool
from result import Result
from time import time
# start_time = time()


def call_result(arg_tuple):
	return Result(*arg_tuple)
def get_dict(result_obj):
	return result_obj.rollNum

if __name__ == "__main__":
	ROll_NUM_LIST = [x for x in range(170994,170998) if not x == 170933]
	pool = Pool(10)
	results = pool.map(call_result,((str(x),'SSC','2','2015') for x in ROll_NUM_LIST))
	pool.close()
	pool.join()
	print results

	pool = Pool(10)
	result_dicts = pool.imap(get_dict,results)
	for result_dict in result_dicts:
		print result_dict
	# print "========seconds=============" , time()-start_time
