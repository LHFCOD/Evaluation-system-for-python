import sys;
#sys.path.append("/public/home/cyp/LHF/python/")
import oracleFunc
import pandas as pd
import numpy as np
from minepy import MINE
import scipy.io as sio
import os
from sklearn.externals import joblib

def ConstructStr():
    measure_rs=oracleFunc.QueryData('select * from lhf_tb_measure where useful!=0')
    sqlstr='select cytime'
    coal_index=oracleFunc.GetIndexFromName('供电煤耗率')
    for index,row in measure_rs.iterrows():
        sqlstr=sqlstr+',V'+str(row['SAVEINDEX'])
    tempstr=" from tb_nx_his_run where v%d between 250 and 310 and cytime between '2015-02-07 00:00:00' and '2015-02-08 00:00:00' order by cytime"%(coal_index)
    sqlstr=sqlstr+tempstr
    return sqlstr

curDir=os.getcwd()
newDir=curDir+'/output'
isExists=os.path.exists(newDir)
if not isExists:
    os.makedirs(newDir)
    print(newDir+'创建成功')
else:
    print(newDir+'路径已存在')

sqlstr=ConstructStr()
realData=oracleFunc.QueryData(sqlstr)
parent_rs=oracleFunc.QueryData('select parent from lhf_tb_measure where useful =1 and parent>0 group by parent')
nKind=parent_rs.shape[0]
measure_rs=oracleFunc.QueryData('select * from lhf_tb_measure where useful=1')
evaluate=[]
evaluateDetail=[]
for index,row in realData.iterrows():
    iT=oracleFunc.GetIndexFromName('送风机A入口温度')
    iP=oracleFunc.GetIndexFromName('#5机组发电机功率')
    TVal=row['V'+str(iT)]
    PVal=row['V'+str(iP)]
    clf=joblib.load('/public/home/cyp/LHF/python/cond/output/'+'cond.m')
    condLabels=clf.predict([[TVal,PVal]])
    condLabels=condLabels[0]
    timeEval=[]
    timeDetail=[]
    for iParent,rowParent in parent_rs.iterrows():
        idParent=rowParent['PARENT']
        kind_rs=measure_rs.loc[measure_rs.PARENT==idParent]

        nameParent=measure_rs.loc[measure_rs.ID==idParent]
        nameParent=nameParent.loc[:,'NAME']
        nameParent=nameParent.values
        nameParent=nameParent[0]
        nameParent=np.array([nameParent])

        score=0
        sumWeight=0
        detail=[]
        for iParam,rowParam in kind_rs.iterrows():
            idParam=rowParam['ID']
            name=rowParam['NAME']
            saveindex=rowParam['SAVEINDEX']
            value=row['V'+str(saveindex)]
            rf=joblib.load('/public/home/cyp/LHF/python/RefVal/output/'+str(idParam))
            refVal=rf.predict([[TVal,PVal]])
            refVal=refVal[0]
            matData=sio.loadmat('/public/home/cyp/LHF/python/weight/output/'+name+'.mat')
            weightMatrix=matData['weight']
            weight=weightMatrix[condLabels][1]
            maxVal=weightMatrix[condLabels][2]
            offset=abs((value-refVal)/(maxVal-refVal))
            temp_score=(1-offset)*weight
            score=score+temp_score
            sumWeight=sumWeight+weight
            temp_detail=[idParam,refVal,maxVal,weight,value,offset,temp_score]
            detail.append(temp_detail)
        stdScore=score/sumWeight
        timeEval.append([idParent,stdScore,score,sumWeight])
        timeDetail.append([[idParent],np.array(detail)])
    evaluate.append(np.array(timeEval))
    evaluateDetail.append(np.array(timeDetail))
sio.savemat('output/monitor.mat',{'evaluate':evaluate,'evaluateDetail':evaluateDetail})
