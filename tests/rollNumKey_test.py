from post_request import get_result

# {'regNum': u'10025-23961-2013', 'examType': u'ANNUAL', 'rollNum': u'170988', 'degree': u'SECONDARY SCHOOL CERTIFICATE ', 'year': u'2015', 'group': u'SCIENCE'} 

result = get_result('170988','SSC','2','2015')
assert result['rollNum'] == '170988'
assert result['regNum']  == '10025-23961-2013'
print result['degree']
assert result['degree']  == 'SECONDARY SCHOOL CERTIFICATE'
assert result['examType'] == 'ANNUAL'
assert result['group'] == 'SCIENCE'
