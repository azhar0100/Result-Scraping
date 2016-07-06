#!/usr/bin/env python
import logging
from result import Result
import json
import sqlite3
conn = sqlite3.connect('/home/azhar/db/rollNumFile.sqlite')

logging.basicConfig(level=logging.INFO)
rollnum = 100166
R = Result(rollnum,'SSC','2','2015',html=conn.execute('''SELECT html FROM rollnums WHERE rollnum = {}'''.format(rollnum)).fetchone()[0])
print R.dict
attr_list = ['rollNum','regNum','student_name','father_name','centre','date_of_birth']
print getattr(R,'rollNum')
result_list = [getattr(R,x) for x in attr_list]
result_list.append(json.dumps(R.marks_row))
print (result_list[0:])
