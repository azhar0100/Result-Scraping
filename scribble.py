#!/usr/bin/env python
import logging
from result import Result
import json
import sqlite3
from os import environ
conn = sqlite3.connect('/home/azhar/db/rollNumFile.sqlite')

logging.basicConfig(level=logging.INFO)

def check_roll(rollnum):
	R = Result(rollnum,'SSC','2','2015',html=conn.execute('''SELECT html FROM rollnums WHERE rollnum = {}'''.format(rollnum)).fetchone()[0])
	with open("{}/{}.html".format(environ['TESTHTML'],rollnum),'w') as f:
		f.write(R.html)
	print "The dict is :", R.dict
	attr_list = ['rollNum','regNum','student_name','father_name','centre','date_of_birth']
	result_list = [R.dict[x] for x in attr_list]
	result_list.append(json.dumps(R.marks_row))
	print (result_list[0:])
rollnums = [100166,100101,115431]
for rollnum in rollnums:
	check_roll(rollnum)
