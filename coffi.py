def GetIndexFromName(cursor,name):
	str="select saveindex from lhf_tb_measure where useful=1 and name='"+name+"'"
	cursor.execute(str)
	rs=cursor.fetchall()
	if len(rs)!=1:
		return None
	else:
		return rs[0][0]

def QueryData(cursor,strSql):
	cursor.execute(strSql)
	data=pd.DataFrame(cursor.fetchall())
	return data

import cx_Oracle
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans

import numpy as np
from sklearn import metrics
from scipy.stats import kstest
from minepy import MINE
import scipy.io as sio
import copy
from sklearn.preprocessing import StandardScaler

tns=cx_Oracle.makedsn('202.204.75.100',1521,'orcl10g')
db=cx_Oracle.connect('imsoft','imsoft',tns)
cursor=db.cursor()
cursor.execute("select saveindex from lhf_tb_measure where name ='供电煤耗率'")
coal_index=(cursor.fetchone())[0]#获取煤耗存储索引
measure_rs=QueryData(cursor,'select name,saveindex from lhf_tb_measure where useful=1')

mine=MINE()####进行最大信息系数分析
#mArray=[]
###新建CSV文件
import csv
with open('coffi.csv','w') as csvfile:
    fieldnames = ['name', 'coffi']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    scaler = StandardScaler()##新建标准化器
    for index,row in measure_rs.iterrows():
        name=row[0]
        saveindex=row[1]
        strSql='select v%d,v%d from tb_nx_his_run where v%d between 250 and 310'%(coal_index,saveindex,coal_index)
        rs=QueryData(cursor,strSql)

        len_rs=40000
        if len(rs)>len_rs:
            rs=rs.sample(n=len_rs)
        else:
            rs=rs.sample(frac=1)
        coal=rs[:][0]
        param=rs[:][1]
        new_coal=scaler.fit_transform(coal.values.reshape(1,-1))
        new_param=scaler.fit_transform(param.values.reshape(1,-1))
        mine.compute_score(new_coal.flatten(),new_param.flatten())
        temp_coffi=mine.mic()
        writer.writerow({'name':name,'coffi':temp_coffi})
        #mArray.append(mine.mic())
#out_rs=copy.deepcopy(measure_rs)##对表格深拷贝
#out_rs.columns=('name','coffi')
#out_rs.loc[:,'coffi']=mArray##简单的引用mArray，赋给第二列
#out_rs.to_csv('coffi.csv',index=False)
#sio.savemat('coffi.mat',{'name':measure_rs[:][0],'mArray':mArray})
