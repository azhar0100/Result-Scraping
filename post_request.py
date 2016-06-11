#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup

url = 'http://result.biselahore.com/Home/Result'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
# params = { 'degree': 'SSC' , 'rollNum': '' , 'session': '2' , 'year': '2015' }

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

	roll_and_reg_row = middle_table('tr',recursive=False)[1].td.table.tr
	result_dict.update({
		"rollNum" : get_tag_contents(roll_and_reg_row)[0].h5.u.string.strip() ,
		"regNum"  : get_tag_contents(roll_and_reg_row)[2].p.u.string.strip()
	})



	return result_dict
