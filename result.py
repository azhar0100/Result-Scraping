#!/usr/bin/env python

import re
import requests
from datetime import datetime,date
from bs4 import BeautifulSoup
from lib import lazy_property,ThrowAwayProperty,DependantProperty
import logging
import collections

url = 'http://result.biselahore.com/Home/Result'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
# params = { 'degree': 'SSC' , 'rollNum': '' , 'session': '2' , 'year': '2015' }

logger = logging.getLogger(__name__)
logger.setLevel(8)
file_handler = logging.FileHandler("result.log")
file_handler.setLevel(8)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

def lowerdebug(msg):
	logger.log(9,msg)

class StudentNotFound(Exception):

	def __init__(self,arg):
		Exception.__init__(self,arg)

def get_html_response(rollNum,degree,session,year):
	params = { 'degree': degree , 'rollNum': rollNum , 'session': session , 'year': year }
	result = requests.post(url , data=params , headers=headers, timeout=30, allow_redirects=False)
	if not result.status_code == 302:
		return result
	else:
		raise StudentNotFound("Redirected to error")

def get_tag_contents(bs4_tag):
	"""Function to get the children of bs4_tag which are tags and not NavigableString"""
	return bs4_tag(True,recursive=False)


class BaseResult(object):

	def __init__(self,rollNum,degree,session,year,html=''):
		if html == '':
			self.html = get_html_response(repr(rollNum).zfill(6),repr(degree),repr(session),repr(year)).text
		else:
			self.html = html
		self.rollNum = rollNum
		self.degree = degree
		self.session = session
		self.year = year

	@ThrowAwayProperty
	def soup(self):
		return BeautifulSoup(self.html,'lxml')

	@soup.dependency
	def middle_table(self):
		return self.soup.select(".td2")[0].table

	@middle_table.dependency
	def reg_row(self):
		return self.middle_table('tr',recursive=False)[1].td.table.tr

	@reg_row.dependency
	def regNum(self):
		try:
			return get_tag_contents(self.reg_row)[2].p.u.string.strip()
		except AttributeError:
			return None

	@middle_table.dependency
	def degree_row(self):
		return self.middle_table('tr',recursive=False)[2].select('h4')[0]

	@degree_row.dependency
	def degree_and_exam_str(self):
		return list(self.degree_row.stripped_strings)[0]
	
	@degree_and_exam_str.dependency
	def examType(self):
		return re.search(r'\(([^()]+)\)',self.degree_and_exam_str).groups()[0].strip()

	@degree_row.dependency
	def group(self):
		return self.degree_row.select('u')[1].string.strip()

	@middle_table.dependency
	def credential_row(self):
		return self.middle_table('tr',recursive=False)[3].table
		

	@credential_row.dependency
	def date_of_birth(self):
		try:
			return datetime.strptime(get_tag_contents(self.credential_row.find_all('tr',recursive=False)[2].find_all('td',recursive=False)[1])[0].string ,"%d/%m/%Y").date()
		except TypeError:
			return None

	@credential_row.dependency
	def centre(self):
		return unicode(get_tag_contents(self.credential_row.find_all('tr',recursive=False)[3].find_all('td',recursive=False)[1])[0].string)

	@credential_row.dependency
	def student_name(self):
		return unicode(get_tag_contents(self.credential_row.find_all('tr',recursive=False)[0].find_all('td',recursive=False)[1])[0].string)

	@credential_row.dependency
	def father_name(self):
		return unicode(get_tag_contents(self.credential_row.find_all('tr',recursive=False)[1].find_all('td',recursive=False)[1])[0].string)

	def __dict__(self):
		attrs = ['rollNum','regNum','examType','group','date_of_birth','centre','student_name','father_name']
		return {x:getattr(self,x) for x in attrs}

	@lazy_property
	def dict(self):
		return self.__dict__()

	# def __getattr__(self,name):
	# 	try:
	# 		return self.dict[name]
	# 	except KeyError:
	# 		raise AttributeError

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
		subjects = {}
		if not marks_row.find_all('tr',recursive=False)[3:-1]:
			return {}

		total_sessions = set()
		for marks_rec in marks_row.find_all('tr',recursive=False)[3:-1]:
			marks_rec_td = marks_rec.find_all('td',recursive=False)
			subject_name = marks_rec_td[0].string.strip()
			logger.debug("Started for subject: {}".format(subject_name))
			subjects[subject_name] = {}
			subject = subjects[subject_name]
			sessions = collections.OrderedDict()

			obtained_iter = zip([x.string.strip() for x in marks_rec_td[4:8]],['p1','p2','pr','total'])
			lowerdebug("Iterating over {} for obtained marks.".format(obtained_iter))
			for marks,level in obtained_iter:
				# marks_rec_td[4:6] contains the obtained marks for p1,p2 and total
				# if marks == '---':
				# 	logger.log(9,"Ignoring for subject {} in {} as it contains:{}".format(subject_name,level,marks))
				# 	continue
				if True:
					logger.log(9,"Found {} obtained for subject {} in {}".format(marks,subject_name,level))
					try:
						int(marks)
						subject[level]={}
						subject[level]['obtained'] = int(marks)
						sessions[level] = None
						logger.log(8,"Putting {} obtained for subject {} in {} as int".format(marks,subject_name,level))
					except ValueError:
						if level == 'pr' and not marks == '---' :
							subject[level]={}
							subject[level]['grade'] = marks
							logger.log(8,"Putting {} obtained for subject {} in {} as grade".format(marks,subject_name,level))
						elif level == 'total':
							subject[level]={}
							subject[level]['obtained'] = sum([x[1]['obtained'] for x in subject.items() if 'obtained' in x[1].keys()])
							sessions[level] = None
							logger.log(8,"Total value of obtained marks not found for subject:{}.Putting calculated value {}".format(subject_name,subject[level]['obtained']))
			
			total_tuple = tuple((int(x) for x in re.split(r'[+=]',marks_rec_td[1].string))) + (marks_rec_td[2].string,)

			if len(total_tuple) == 2:
				logger.log(9,"Subject {} has only a 2-tuple : {}".format(subject_name,total_tuple))
				for key in sessions:
					session = subject[key]
					session['total'] = total_tuple[0]
					logger.log(8,"Putting total marks {} for subject {} in session {}".format(total_tuple[0],subject_name,key))
			else:
				logger.log(9,'total_tuple is {}'.format(total_tuple))
				for x,y in zip(['p1','p2','total','pr'],total_tuple):
					try:
						subject[x]['total'] = int(y)
						logger.log(8,"Putting {} total for subject {} in {}".format(y,subject_name,x))
					except KeyError:
						continue
					except ValueError:
						continue
			for session in sessions:
				x = subject[session]
				x['pass'] = not (float(x['obtained']) / float(x['total'])) < (1.0/3.0)
				logger.log(8,"Putting pass status {} for subject {} in {} ".format(x['pass'],subject_name,session))

			total_sessions.update(sessions.keys())
			logger.debug("Finished the result for subject:{} as sessions are {} and total are ".format(subject_name,sessions.keys()))

		logger.debug("Finished obtaining result for subjects.")
		def total_marks(subjects):
			return tuple(map(lambda x,y:x(y),
				[sum,sum,lambda x:reduce(lambda y,z: y and z,x)]
				,zip(*[x[1] for x in subjects.items()])))

		def filter_out_grade(x):
			check_list = ['obtained','total','pass']
			return set(check_list) <= set(x.keys())

		total_dict = {k:{
		'obtained' : [],
		'total'    : [],
		'pass'     : []
		} for k in total_sessions}

		logger.debug("Total Dict Formed is {} as total sessions found are {}".format(total_dict,total_sessions))
		for subject_name,subject_dict in subjects.items():
			logger.log(7,"Started collection In Subject {}:{}".format(subject_name,subject_dict))
			for session,marks in {k:v for (k,v) in subject_dict.items() if filter_out_grade(v)}.items():
				logger.log(8,"Starting total collection on session {} in subject {}".format(session,subject_name))
				total_dict[session]['obtained'].append(marks['obtained'])
				total_dict[session]['total'].append(marks['total'])
				total_dict[session]['pass'].append(marks['pass'])

		logger.debug(total_dict)
		total_dict = {i:{k:f(total_dict[i][k]) for (k,f) in zip(['obtained','total','pass'],[sum,sum,lambda x:reduce(lambda y,z: y and z,x)])} for i in [x for x in total_dict.keys() if not x == 'pr']}
		logger.debug("Obtained the totals {}".format(total_dict))

		return {
			'total' : total_dict,
			'subjects' : subjects
		}


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
	# Retained for backward compatibility
	if session == 0:
		return BaseResult(rollNum,degree,session,year)
	if session == 1:
		return Result_part1(rollNum,degree,session,year,html=html)
	if session == 2:
		return Result_part2(rollNum,degree,session,year,html=html)
	