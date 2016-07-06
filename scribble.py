#!/usr/bin/env python
import logging
from result import Result
import json

logging.basicConfig(level=logging.INFO)
R = Result('109243','SSC','2','2015',html=open("../ReqResult.htm",'r').read())
print R.dict
attr_list = ['rollNum','regNum','student_name','father_name','centre','date_of_birth']
print getattr(R,'rollNum')
result_list = [getattr(R,x) for x in attr_list]
result_list.append(json.dumps(R.marks_row))
print (result_list[0:])
