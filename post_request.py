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
	
def get_result(rollNum,degree,session,year):
	html_response = get_html_response(rollNum,degree,session,year)
	result_soup = BeautifulSoup(html_response.text)
	result_dict = {}

	# The result page has two tables , one to the left and other to the right.
	# The page uses an ancient table layout.The middle one has the actual data.
	# The middle_table is divided into many <tr> elements which are handled separately.

	middle_table = result_soup.select(".td2")[0].table

	reg_row = middle_table('tr',recursive=False)[1].td.table.tr
	result_dict.update({
		"rollNum" : get_tag_contents(reg_row)[0].h5.u.string.strip() ,
		"regNum"  : get_tag_contents(reg_row)[2].p.u.string.strip()
	})

	degree_row = middle_table('tr',recursive=False)[2].select('h4')[0]
	degree_and_exam_str = list(degree_row.stripped_strings)[0]
	result_dict.update({
		"degree"   : re.search(r'([^()]+)\(',degree_and_exam_str).groups()[0].strip() ,
		"examType" : re.search(r'\(([^()]+)\)',degree_and_exam_str).groups()[0].strip() ,
		"year"     : datetime.strptime(degree_row.u.string.strip(),"%Y").date() ,	
		"group"    : degree_row.select('u')[1].string.strip()
	})

	credential_row = middle_table('tr',recursive=False)[3].table

	result_dict.update({
		"student_name" : unicode(get_tag_contents(credential_row.find_all('tr',recursive=False)[0].find_all('td',recursive=False)[1])[0].string),
		"father_name"  : unicode(get_tag_contents(credential_row.find_all('tr',recursive=False)[1].find_all('td',recursive=False)[1])[0].string),
		"centre"       : unicode(get_tag_contents(credential_row.find_all('tr',recursive=False)[3].find_all('td',recursive=False)[1])[0].string)
	})
	result_dict["date_of_birth"] = datetime.strptime(get_tag_contents(credential_row.find_all('tr',recursive=False)[2].find_all('td',recursive=False)[1])[0].string,"%d/%m/%Y").date()

	marks_row = middle_table('tr',recursive=False)[4].td
	print marks_row

	return result_dict

class Result(object):

	def __init__(self,rollNum,degree,session,year):
		html_response = get_html_response(rollNum,degree,session,year)
		self.soup = BeautifulSoup(html_response.text)
		self.middle_table = self.soup.select(".td2")[0].table

	@lazy_property
	def reg_row(self):
		middle_table = result_soup.select(".td2")[0].table
		reg_row = middle_table('tr',recursive=False)[1].td.table.tr
		rollNum = get_tag_contents(reg_row)[0].h5.u.string.strip()
		regNum  = get_tag_contents(reg_row)[2].p.u.string.strip()
		return (rollNum,regNum)

	@lazy_property
	def rollNum(self):
		return self.reg_row[0]

	@lazy_property
	def regNum(self):
		return self.reg_row[1]

