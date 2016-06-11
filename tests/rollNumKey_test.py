from post_request import get_result

result = get_result('170988','SSC','2','2015')
assert result['rollNum'] == '170988'
assert result['regNum']  == '10025-23961-2013'
