
import pandas as pd
def GetIndexFromName(name):
	global cursor
	sqlstr="select saveindex from lhf_tb_measure where name='"+name+"'"
	cursor.execute(sqlstr)
	rs=cursor.fetchall()
	if len(rs)!=1:
		return None
	else:
		return rs[0][0]

def QueryData(strSql):
	global cursor
	cursor.execute(strSql)
	data=pd.DataFrame(cursor.fetchall())
	title=[i[0] for i in cursor.description]
	data.columns=title
	return data

import cx_Oracle
tns=cx_Oracle.makedsn('202.204.75.100',1521,'orcl10g')
db=cx_Oracle.connect('imsoft','imsoft',tns)
cursor=db.cursor()
