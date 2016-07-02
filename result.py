#!/usr/bin/env python

import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import logging

url = 'http://result.biselahore.com/Home/Result'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
# params = { 'degree': 'SSC' , 'rollNum': '' , 'session': '2' , 'year': '2015' }

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
file_handler = logging.FileHandler("result.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

def lazy_property(fn):
	attr_name = '__lazy__' + fn.__name__

	@property
	def _lazy_property(self):
		if not hasattr(self,attr_name):
			setattr(self,attr_name,fn(self))
		return getattr(self,attr_name)

	return _lazy_property

def get_html_response(rollNum,degree,session,year):
	params = { 'degree': degree , 'rollNum': rollNum , 'session': session , 'year': year }
	return requests.post(url , data=params , headers=headers, timeout=30)

def get_tag_contents(bs4_tag):
	"""Function to get the children of bs4_tag which are tags and not NavigableString"""
	return bs4_tag(True,recursive=False)

class StudentNotFound(Exception):

	def __init__(self,arg):
		Exception.__init__(self,arg)

class BaseResult(object):

	def __init__(self,rollNum,degree,session,year,html=''):
		if html == '':
			self.html = get_html_response(rollNum,degree,session,year).text
		else:
			self.html = html
		if re.search(r'Student not found.',self.html):
			raise StudentNotFound("Student Not Found for this data")
		self.rollNum = rollNum
		self.degree = degree
		self.session = session
		self.year = year

	@lazy_property
	def soup(self):
		return BeautifulSoup(self.html,'lxml')

	@lazy_property
	def middle_table(self):
		return self.soup.select(".td2")[0].table

	@lazy_property
	def reg_row(self):
		reg_row = self.middle_table('tr',recursive=False)[1].td.table.tr
		regNum  = get_tag_contents(reg_row)[2].p.u.string.strip()
		return {"regNum":regNum}

	@lazy_property
	def degree_row(self):
		degree_row = self.middle_table('tr',recursive=False)[2].select('h4')[0]
		degree_and_exam_str = list(degree_row.stripped_strings)[0]
		return {
			"examType" : re.search(r'\(([^()]+)\)',degree_and_exam_str).groups()[0].strip() ,
			"group"    : degree_row.select('u')[1].string.strip()
		}

	@lazy_property
	def credential_row(self):
		credential_row = self.middle_table('tr',recursive=False)[3].table

		return {
			"student_name" : unicode(get_tag_contents(credential_row.find_all('tr',recursive=False)[0].find_all('td',recursive=False)[1])[0].string),
			"father_name"  : unicode(get_tag_contents(credential_row.find_all('tr',recursive=False)[1].find_all('td',recursive=False)[1])[0].string),
			"centre"       : unicode(get_tag_contents(credential_row.find_all('tr',recursive=False)[3].find_all('td',recursive=False)[1])[0].string),
			"date_of_birth": datetime.strptime(get_tag_contents(credential_row.find_all('tr',recursive=False)[2].find_all('td',recursive=False)[1])[0].string ,"%d/%m/%Y").date()
		}

	
	@property
	def dict(self):
		result_dict = {}
		result_dict.update(self.reg_row)
		result_dict.update(self.degree_row)
		result_dict.update(self.credential_row)
		return result_dict

	def __getattr__(self,name):
		try:
			return self.dict[name]
		except KeyError:
			raise AttributeError

class ResultMarks(BaseResult):

	@lazy_property
	def marks_row(self):
		raise NotImplementedError

	@property
	def dict(self):
		result_dict = BaseResult.dict.fget(self)
		result_dict.update(self.marks_row)
		return result_dict

class Result_part2(ResultMarks):

	@lazy_property
	def marks_row(self):
		def convert_to_int(n):
			try:
				return int(n)
			except ValueError:
				return 0
		marks_row = self.middle_table('tr',recursive=False)[4].td.table
		logger.debug("Obtained the middle table.")
		subjects = {
			'p1' : {},
			'p2' : {},
			'total' : {}
		}
		if not marks_row.find_all('tr',recursive=False)[3:-1]:
			return {}

		for marks_rec in marks_row.find_all('tr',recursive=False)[3:-1]:
			marks_rec_td = marks_rec.find_all('td',recursive=False)
			subject_name = marks_rec_td[0].string.strip()
			( total_p1,total_p2,total_total ) = tuple((int(x) for x in re.split(r'[+=]',marks_rec_td[1].string)))

			( obtained_p1,obtained_p2) = tuple([convert_to_int(x) for x in [x.string for x in marks_rec_td[4:6]]])
			obtained_total = obtained_p1 + obtained_p2

			pass_status_p1 = (obtained_p1/total_p1) > (float(1)/float(3))
			pass_status_p2 = (obtained_p2/total_p2) > (float(1)/float(3))
			pass_status_total = pass_status_p1 and pass_status_p2

			subjects['p1'][subject_name] = (obtained_p1,total_p1,pass_status_p1)
			subjects['p2'][subject_name] = (obtained_p2,total_p2,pass_status_p2)
			subjects['total'][subject_name] = (obtained_total,total_total,pass_status_total)

			pass_status_observed =  marks_rec_td[8].string.strip() == 'PASS'
			logger.debug("Finished the result for subject:{}".format(subject_name))

		logger.debug("Finished obtaining result for subjects.")
		def total_marks(subjects):
			return tuple(map(lambda x,y:x(y),
				[sum,sum,lambda x:reduce(lambda x,y: x and y,x)]
				,zip(*[x[1] for x in subjects.items()])))

		totals = dict(zip(['p1','p2','total'],[total_marks(subjects[x]) for x in ['p1','p2','total']]))
		logger.debug("Obtained the totals")

		return {x:(totals[x],subjects[x]) for x in ['p1','p2','total'] }


class Result_part1(ResultMarks):

	@lazy_property
	def marks_row(self):
		marks_row = self.middle_table('tr',recursive=False)[4].td.table
		subjects = {}
		for marks_rec in marks_row.find_all('tr',recursive=False)[3:-1]:
			marks_rec_td = marks_rec.find_all('td',recursive=False)
			subject_name = marks_rec_td[0].string.strip()
			total_marks = int(marks_rec_td[1].string.strip())
			obtained_marks = int(marks_rec_td[2].string.strip())
			pass_status = marks_rec_td[3].string.strip() == 'PASS'
			subjects[subject_name] = (obtained_marks,total_marks,pass_status)
		obtained_marks = sum([x[1][0] for x in subjects.items()])
		total_marks    = sum([x[1][1] for x in subjects.items()])
		pass_status    = not False in [x[1][2] for x in subjects.items()]
		return {
			'subjects' : subjects ,
			'marks'    : (obtained_marks,total_marks,pass_status)
		}


def Result(rollNum,degree,session,year,html=''):
	if session == '1':
		return Result_part1(rollNum,degree,session,year,html=html)
	if session == '2':
		return Result_part2(rollNum,degree,session,year,html=html)
	