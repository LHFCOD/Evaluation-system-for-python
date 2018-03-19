def GetIndexFromName(cursor,name):
	str="select saveindex from tb_nx_measure where name='"+name+"'"
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
import scipy.io as sio

from sklearn.externals import joblib
import os
curDir=os.getcwd()
newDir=curDir+'/output'
isExists=os.path.exists(newDir)
if not isExists:
	os.makedirs(newDir)
	print(newDir+'创建成功')
else:
	print(newDir+'路径已存在')

tns=cx_Oracle.makedsn('202.204.75.100',1521,'orcl10g')
db=cx_Oracle.connect('imsoft','imsoft',tns)
cursor=db.cursor()
iT=GetIndexFromName(cursor,'送风机A入口温度')
iP=GetIndexFromName(cursor,'#5机组发电机功率')
coal_index=GetIndexFromName(cursor,'供电煤耗')
strSql="select id,v%d,v%d from tb_nx_his_run where v%d between 250 and 310" % (iT,iP,coal_index)
condData=QueryData(cursor,strSql)
condData.columns=('id','T','P')#给数据表添加标题
condData=condData.loc[(condData['T']>-5) & (condData['T']<40) & (condData['P']>500) & (condData['P']<1200)]
##########K均值聚类
###对样本进行采样
##sampData=condData.sample(n=100000)
clf=KMeans(n_clusters=80)
clf.fit(condData.loc[:,['T','P']])
joblib.dump(clf,'output/cond.m')
condData['labels']=clf.labels_
####id T P labels
sio.savemat('output/cond.mat',{'condData':condData.values})
