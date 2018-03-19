import sys;
sys.path.append("/public/home/cyp/LHF/python/")
import oracleFunc
import pandas as pd
import numpy as np
from minepy import MINE
import scipy.io as sio
import os
measure_rs=oracleFunc.QueryData('select id,name,saveindex,parent from lhf_tb_measure where useful=1')
measure_rs.columns=('id','name','saveindex','parent')
matData=sio.loadmat('/public/home/cyp/LHF/python/RefVal/cond.mat')
condData=pd.DataFrame(matData['condData'])
condData.columns=('id','T','P','labels')
coal_index=oracleFunc.GetIndexFromName('供电煤耗率')
minLabel=int(condData.loc[:,'labels'].min())
maxLabel=int(condData.loc[:,'labels'].max())
mine=MINE()
curDir=os.getcwd()
newDir=curDir+'/output'
isExists=os.path.exists(newDir)
if not isExists:
    os.makedirs(newDir)
    print(newDir+'创建成功')
else:
    print(newDir+'路径已存在')
for index,row in measure_rs.iterrows():
    ##创建二维数组，第一列为工况id，第二列为权重
    measure_out=[]
    name=row['name']
    saveindex=row['saveindex']
    parent=row['parent']
    if not parent >=1:
        continue
    parent_index=measure_rs[measure_rs.id==parent]['saveindex'].iloc[0]
    hisdata=oracleFunc.QueryData('select id,v%d,v%d from tb_nx_his_run where v%d between 250 and 310'%(parent_index,saveindex,coal_index))
    hisdata.columns=('id','parent','param')
    for condLabels in range(minLabel,maxLabel+1):
        temp_condData=condData.loc[condData['labels']==condLabels]
        temp_measure=pd.merge(hisdata,temp_condData,how='inner')
        mine.compute_score(temp_measure.loc[:,'parent'].values,temp_measure.loc[:,'param'].values)
        weight=mine.mic()
        means=temp_measure.loc[:,'param'].mean()
        std=temp_measure.loc[:,'param'].std()
        lower=means-3*std
        upper=means+3*std
        maxVal=abs(lower)
        if maxVal<abs(upper):
            maxVal=abs(upper)
        measure_out.append([condLabels,weight,maxVal,lower,upper])
    sio.savemat('output/'+name,{'weight':measure_out})
