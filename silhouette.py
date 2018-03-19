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
import scipy.io as sio
import numpy as np
from sklearn import metrics
from scipy.stats import kstest
#import os
#os.environ['NLS_LANG']='SIMPLIFIED CHINESE_CHINA.ZHS16GBK'
#import sys
#reload(sys)
#sys.setdefaultencoding('GBK') 

tns=cx_Oracle.makedsn('202.204.75.100',1521,'orcl10g')
db=cx_Oracle.connect('imsoft','imsoft',tns)
cursor=db.cursor()
iT=GetIndexFromName(cursor,'送风机A入口温度')
iP=GetIndexFromName(cursor,'#5机组发电机功率')
strSql="select v%d,v%d from tb_nx_his_run" % (iT,iP)
condData=QueryData(cursor,strSql)
condData.columns=('T','P')#给数据表添加标题
condData=condData.loc[(condData['T']>-5) & (condData['T']<40) & (condData['P']>500) & (condData['P']<1200)]
##########K均值聚类
sil=[]#轮廓系数
for K in range(2,100):
	###对样本进行采样
	sampData=condData.sample(n=10000)
	#clf=KMeans(n_clusters=K)
	#y_label=clf.fit(sampData).labels_
	y_label=DBSCAN(eps=0.5).fit_predict(sampData)
	silCoffi=metrics.silhouette_score(sampData,y_label)
	sil.append(silCoffi)
	#test_stat=kstest(sampData.loc[:,'T'],'uniform')
	#y_label=DBSCAN(eps=0.5).fit_predict(sampData)
	#print("Silhouette Coefficient: %0.3f"% metrics.silhouette_score(sampData,y_label))
########等间距划分
nSamp=10000
sampData=condData.sample(n=nSamp)
sampData.reset_index(drop=True,inplace=True)
minT=sampData['T'].min()
maxT=sampData['T'].max()
minP=sampData['P'].min()
maxP=sampData['P'].max()
nT=20
nP=100
wT=(maxT-minT)/nT
wP=(maxP-minP)/nP
y_label=np.zeros((nSamp,1),dtype=np.int32)
for index in range(0,nSamp):
	iT=int((sampData['T'][index]-minT)/wT)
	iP=int((sampData['P'][index]-minP)/wP)
	y_label[index,0]=iP+iT*nT
###轮廓系数
ysil=metrics.silhouette_score(sampData,y_label)
sio.savemat('save1.mat',{'sampData':sampData.values,'y_label':y_label,'ysil':ysil})
###字符编码出现错误，可以退出python，在linux系统中导入 export LANG=zh_CN.gb2312，即可

	silCoffi=metrics.silhouette_score(sampData,y_label)
	sil.append(silCoffi)
	#test_stat=kstest(sampData.loc[:,'T'],'uniform')
	#y_label=DBSCAN(eps=0.5).fit_predict(sampData)
	#print("Silhouette Coefficient: %0.3f"% metrics.silhouette_score(sampData,y_label))

sio.savemat('save.mat',{'sampData':sampData.values,'y_label':y_label,'sil':sil})
###字符编码出现错误，可以退出python，在linux系统中导入 export LANG=zh_CN.gb2312，即可




#########################################33
import pandas as pd
from sklearn.cluster import DBSCAN
import scipy.io as sio
import numpy as np
from sklearn import metrics

matData=sio.loadmat('save.mat')
condData=pd.DataFrame(matData['condData'])
###对样本进行采样
sampData=condData.sample(n=100000)
y_label=DBSCAN(eps=0.5).fit_predict(sampData)
#print("Silhouette Coefficient: %0.3f"% metrics.silhouette_score(sampData,y_label))

 x = np.random.normal(0,1,1000)
test_stat=kstest(x,'norm')
print(test_stat)

count=0
for K in range(1,10):
	print(K)



