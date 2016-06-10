#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup

url = 'http://result.biselahore.com/Home/Result'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
# params = { 'degree': 'SSC' , 'rollNum': '' , 'session': '2' , 'year': '2015' }

def get_html_response(rollNum,degree,session,year):
	params = { 'degree': degree , 'rollNum': rollNum , 'session': session , 'year': year }
	return requests.post(url , data=params , headers=headers)
	
def get_result(rollNum,degree,session,year):
	html_response = get_html_response(rollNum,degree,session,year)
	result_soup = BeautifulSoup(html_response.text)
	result_dict = {
		rollNum : result_soup.select(".td2  h5 > u")[0].string
	}

	return result_dict
