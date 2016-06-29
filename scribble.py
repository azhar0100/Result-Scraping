from result import Result
R = Result('171023','SSC','2','2015',html=open("../ReqResult.htm",'r').read())
rd = R.dict
print rd
