from sklearn.cluster import KMeans
import numpy as np
import pandas as pd
import csv
import scipy.io as sio
import os

import oracleFunc
from sklearn.ensemble import RandomForestRegressor
from sklearn.externals import joblib
coal_index=oracleFunc.GetIndexFromName('供电煤耗率')
strSql='select id,v%d from tb_nx_his_run where v%d between 250 and 310'%(coal_index,coal_index)
coal_rs=oracleFunc.QueryData(strSql)
coal_rs.columns=('id','coal')

condmat=sio.loadmat('cond.mat')
condData=pd.DataFrame(condmat['condData'])
condData.columns=('id','T','P','labels')#给数据表添加标题
minLabel=int(condData.loc[:,'labels'].min())
maxLabel=int(condData.loc[:,'labels'].max())

curDir=os.getcwd()
newDir=curDir+'/output'
isExists=os.path.exists(newDir)
if not isExists:
    os.makedirs(newDir)
    print(newDir+'创建成功')
else:
    print(newDir+'路径已存在')

for i in range(minLabel,maxLabel+1):
    temp_condData=condData.loc[condData['labels']==i]
    ##寻找工况为i的煤耗
    cond_param=pd.merge(coal_rs,temp_condData,how='inner')
    clf=KMeans(n_clusters=3)
    clf.fit(cond_param.loc[:,'coal'].values.reshape(-1,1))
    cond_param['class']=clf.labels_
    min_class=np.where(clf.cluster_centers_==np.min(clf.cluster_centers_))[0][0]
    min_rs=cond_param.loc[cond_param['class']==min_class]
    if i==0:
        minAll=min_rs
    else:
        minAll=pd.merge(min_rs,minAll,how='outer')###对所有的最低煤耗簇合并

measure_rs=oracleFunc.QueryData('select id,name,saveindex from lhf_tb_measure where useful=1')
measure_rs.columns=['id','name','saveindex']
for index,row in measure_rs.iterrows():
    param_id=row['id']
    name=row['name']
    saveindex=row['saveindex']
    strSql='select id,v%d from tb_nx_his_run where v%d between 250 and 310'%(saveindex,coal_index)###v321是厂用电率
    param_rs=oracleFunc.QueryData(strSql)
    param_rs.columns=('id','param')
    merge_rs=pd.merge(minAll,param_rs,how='inner')##根据选择好的煤耗的那一类选择参数
    ##交叉验证
    # from sklearn.cross_validation import KFold
    # kf = KFold(25, n_folds=5, shuffle=False)
    # train_set = []
    # test_set = []
    # for train, test in skf:
    #     train_set.append(train)
    #     test_set.append(test)

    ###利用随机森林对不同工况的基准值进行预测

    rf=RandomForestRegressor()
    ##shuf_rs=merge_rs.sample(frac=1)

    rf_input=merge_rs.loc[:,['T','P']]
    rf_output=merge_rs.loc[:,'param']
    rf.fit(rf_input,rf_output)
    ##存储基准值模型
    joblib.dump(rf,'output/'+str(param_id))
    #train_pre=rf.predict(rf_input)

    # nT=100
    # nP=500
    # T = np.linspace(10,20,nT)
    # P = np.linspace(500,1000,nP)
    # mT,mP = np.meshgrid(T,P)
    # rT=mT.reshape(-1,1)
    # rP=mP.reshape(-1,1)
    # rInput=np.hstack((rT,rP))
    # test_input=pd.DataFrame(rInput)
    # test_pre=rf.predict(test_input)
    # test_pre=test_pre.reshape(nP,nT)
    #
    # sio.savemat('mat/'+name+'.mat',{'rf_input':rf_input.values,'rf_output':rf_output.values\
    # ,'train_pre':train_pre,'mT':mT,'mP':mP,'test_pre':test_pre})
