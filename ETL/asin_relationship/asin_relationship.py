# -*- coding: utf-8 -*-
"""
@File    :   asin_relationship.py
@Contact :   1421877537@qq.com
@License :   (C)Copyright 2017-2018
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2021/11/30 14:31    leoy        1.0      get father asin data from movie and json...
"""


import json
import pandas as pd

class AsinRelationship:
    
    def __init__(self):
        
        #父子Asin关系
        self.asin_relationship = []
        
        #对应的父Asin版本数量
        self.father_asin_count = []
        
    def loadFile(self,jsonPath,moviePath):
        
        jsonFile = open(jsonPath,'r',encoding = "UTF-8")
        self.asin_relation = json.load(jsonFile)
        movie_data = pd.read_csv(moviePath)
        self.movie_asin = movie_data.loc[:,"asin"].to_list()    


    def getRelationship(self):
        for instance in self.asin_relation:    
            #先去除一行中的TV数据
            for tmp in instance:
                if tmp not in self.movie_asin:
                    instance.remove(tmp)
            
            if len(instance) == 0:
                continue
                
            father = instance[0]
            for item in instance:
                relation = {"asin":str(item),"father_asin":str(father)}
                self.asin_relationship.append(relation)
            count = len(instance)
            c = {"father_asin":str(father),"count":count}
            self.father_asin_count.append(c)
    
    def printData(self,path1,path2):
        
        asin_relationship_df = pd.DataFrame(self.asin_relationship)
        father_asin_count_df = pd.DataFrame(self.father_asin_count)
        asin_relationship_df.to_csv(path1,index=False)
        father_asin_count_df.to_csv(path2,index=False)

"""        
a = AsinRelationship()
a.loadFile("res.json","movie_data.csv")
a.getRelationship()
a.printData()
"""
