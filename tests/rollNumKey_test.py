from post_request import get_result

# {'regNum': u'10025-23961-2013', 'examType': u'ANNUAL', 'rollNum': u'170988', 'degree': u'SECONDARY SCHOOL CERTIFICATE ', 'year': u'2015', 'group': u'SCIENCE'} 

expected = {'regNum': u'10025-23961-2013', 'examType': u'ANNUAL', 'father_name': u'TAHIR MEHMOOD', 'rollNum': u'170988', 'degree': u'SECONDARY SCHOOL CERTIFICATE', 'year': datetime.date(2015, 1, 1), 'date_of_birth': datetime.date(2000, 6, 30), 'group': u'SCIENCE', 'centre': u'ALLAMA IQBAL BOYS HIGH SCHOOL,  53-H CANAL BERG MULTAN ROAD LAHORE ', 'student_name': u'AZHAR TAHIR'}

result = Result('170988','SSC','2','2015').dict
assert result == expected
