from post_request import Result
import datetime

expected = {'regNum': u'10025-23961-2013', 'examType': u'ANNUAL', 'father_name': u'TAHIR MEHMOOD', 'rollNum': u'170988', 'degree': u'SECONDARY SCHOOL CERTIFICATE', 'year': datetime.date(2015, 1, 1), 'date_of_birth': datetime.date(2000, 6, 30), 'group': u'SCIENCE', 'centre': u'ALLAMA IQBAL BOYS HIGH SCHOOL,  53-H CANAL BERG MULTAN ROAD LAHORE ', 'student_name': u'AZHAR TAHIR'}
result = Result('170988','SSC','2','2015').dict
assert result == expected

from post_request import Result_part2
expected = {'examType': u'ANNUAL', 'rollNum': u'170988', 'degree': u'SECONDARY SCHOOL CERTIFICATE', 'centre': u'ALLAMA IQBAL BOYS HIGH SCHOOL,  53-H CANAL BERG MULTAN ROAD LAHORE ', 'marks': (1028, 1100, True), 'regNum': u'10025-23961-2013', 'date_of_birth': datetime.date(2000, 6, 30), 'father_name': u'TAHIR MEHMOOD', 'year': datetime.date(2015, 1, 1), 'group': u'SCIENCE', 'subjects': {u'PAKISTAN STUDIES': (46, 50, True), u'ISLAMIYAT': (40, 50, True), u'COMPUTER SCIENCE': (71, 75, True), u'ENGLISH': (68, 75, True), u'MATHEMATICS': (72, 75, True), u'CHEMISTRY': (71, 75, True), u'PHYSICS': (75, 75, True), u'URDU.': (68, 75, True)}, 'student_name': u'AZHAR TAHIR'}
result = Result_part2('170988','SSC','2','2015').dict
assert result == expected

from post_request import Result_part1
expected = {'examType': u'9TH CLASS', 'rollNum': u'496498', 'degree': u'SECONDARY SCHOOL CERTIFICATE', 'centre': u'SHEIKHUPURA', 'marks': (236, 550, False), 'regNum': u'60671-SP.04-2015', 'date_of_birth': datetime.date(2000, 12, 2), 'father_name': u'MUHAMMAD SALEEM', 'year': datetime.date(2015, 1, 1), 'group': u'SCIENCE', 'subjects': {u'PAKISTAN STUDIES': (29, 50, True), u'ISLAMIYAT': (39, 50, True), u'COMPUTER SCIENCE': (39, 75, True), u'ENGLISH': (27, 75, True), u'URDU': (40, 75, True), u'MATHEMATICS': (11, 75, False), u'CHEMISTRY': (20, 75, False), u'PHYSICS': (31, 75, True)}, 'student_name': u'AGHA MUHAMMAD UZAIR'}
result = Result_part1('496498','SSC','1','2015').dict
assert result == expected
