#!/usr/bin/env python

import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup

url = 'http://result.biselahore.com/Home/Result'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
# params = { 'degree': 'SSC' , 'rollNum': '' , 'session': '2' , 'year': '2015' }

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
	return requests.post(url , data=params , headers=headers)

def get_tag_contents(bs4_tag):
	"""Function to get the children of bs4_tag which are tags and not NavigableString"""
	return bs4_tag(True,recursive=False)

class BaseResult(object):

	def __init__(self,rollNum,degree,session,year):
		html_response = get_html_response(rollNum,degree,session,year)
		if re.search(r'Student not found.',html_response.text):
			raise IndexError("Student Not Found for this data")
		self.soup = BeautifulSoup(html_response.text,'lxml')
		self.middle_table = self.soup.select(".td2")[0].table

	@lazy_property
	def reg_row(self):
		middle_table = self.soup.select(".td2")[0].table
		reg_row = middle_table('tr',recursive=False)[1].td.table.tr
		rollNum = get_tag_contents(reg_row)[0].h5.u.string.strip()
		regNum  = get_tag_contents(reg_row)[2].p.u.string.strip()
		return {"rollNum" : rollNum, "regNum":regNum}

	@lazy_property
	def degree_row(self):
		degree_row = self.middle_table('tr',recursive=False)[2].select('h4')[0]
		degree_and_exam_str = list(degree_row.stripped_strings)[0]
		return {
			"degree"   : re.search(r'([^()]+)\(',degree_and_exam_str).groups()[0].strip() ,
			"examType" : re.search(r'\(([^()]+)\)',degree_and_exam_str).groups()[0].strip() ,
			"year"     : datetime.strptime(degree_row.u.string.strip(),"%Y").date() ,
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
		marks_row = self.middle_table('tr',recursive=False)[4].td.table
		marks_dict = {}
		for marks_rec in marks_row.find_all('tr',recursive=False)[3:-1]:
			marks_rec_td = marks_rec.find_all('td',recursive=False)
			subject_name = marks_rec_td[0].string.strip()
			total_marks = int(re.search(r'.+\+([0-9]+)=.+',marks_rec_td[1].string).groups()[0])
			obtained_marks = int(marks_rec_td[5].string)
			pass_status =  marks_rec_td[8].string.strip() == 'PASS'
			marks_dict[subject_name] = (obtained_marks,total_marks,pass_status)

		total_marks_row =  get_tag_contents(marks_row.find_all('tr',recursive=False)[-1])
		total_marks = int(total_marks_row[1].string)
		# mark_string_groups = re.compile(r'(\S+)').findall(total_marks_row[2].string)
		# pass_status = mark_string_groups[2].strip() == 'PASS'
		# obtained_marks = mark_string_groups[3].strip()
		obtained_marks = sum([x[1][0] for x in marks_dict.items()])
		pass_status    = not False in [x[1][2] for x in marks_dict.items()]

		return {
			'subjects':marks_dict,
			'marks' : (obtained_marks,total_marks,pass_status)
		}

class Result_part1(ResultMarks):

	@lazy_property
	def marks_row(self):
		marks_row = self.middle_table('tr',recursive=False)[4].td.table
		marks_dict = {}
		for marks_rec in marks_row.find_all('tr',recursive=False)[3:-1]:
			marks_rec_td = marks_rec.find_all('td',recursive=False)
			subject_name = marks_rec_td[0].string.strip()
			total_marks = int(marks_rec_td[1].string.strip())
			obtained_marks = int(marks_rec_td[2].string.strip())
			pass_status = marks_rec_td[3].string.strip() == 'PASS'
			marks_dict[subject_name] = (obtained_marks,total_marks,pass_status)
		obtained_marks = sum([x[1][0] for x in marks_dict.items()])
		total_marks    = sum([x[1][1] for x in marks_dict.items()])
		pass_status    = not False in [x[1][2] for x in marks_dict.items()]
		return {
			'subjects' : marks_dict ,
			'marks'    : (obtained_marks,total_marks,pass_status)
		}

def Result(rollNum,degree,session,year):
	if session == '1':
		return Result_part1(rollNum,degree,session,year)
	if session == '2':
		return Result_part2(rollNum,degree,session,year)
	