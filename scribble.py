#!/usr/bin/env python
import logging
from result import Result

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', file='scribblelog.log')
R = Result('100027','SSC','2','2015',html=open("../ReqResult.htm",'r').read())
print R.dict
