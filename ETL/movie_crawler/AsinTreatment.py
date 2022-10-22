# -*- coding: utf-8 -*-
"""
对于asin数据的预处理

Created on Tue Oct 26 20:10:23 2021

@author: 12094
"""
import json
import pandas as pd


class AsinTreatment:
    @staticmethod
    def handle():
        fileName='./Movies_and_TV_5.json'
        asinSet=set()
        
        with open(fileName, 'r', encoding='utf-8') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                s = json.loads(line)
                asinSet.add(s['asin'])
                
        # 写文件，存储为csv文件
        df=pd.DataFrame(asinSet,columns=['asinID'])
        df['hasDeal']=False
        df.to_csv('asin.csv',index=False)
