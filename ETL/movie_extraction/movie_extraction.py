# -*- coding: utf-8 -*-
"""
@File    :   movie_extraction.py
@Contact :   1421877537@qq.com
@License :   (C)Copyright 2017-2018
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2021/11/30 14:31    leoy        1.0      get extraction data column from cleaning data...
"""


# import lib 
import pandas as pd
import re

# define class 
class Extraction:
    
    def __init__(self):
        #数据源
        self.consolidation = pd.DataFrame()
        
        #删除字符列表
        self.dropList = []
             
    def loadDataSource(self,path,dropList):
        self.consolidation = pd.read_excel(path)
        self.dropList = dropList.copy()
        
    
    def splitAndDropDulplication(self, tagList):
        
        self.consolidation.loc[:,tagList].fillna("",inplace = True)
        result_with_tag = {}
        for tag in tagList:
            # 定义一个结果列表、切片合并数据源获得对应Series
            result = []
            data_with_tag = self.consolidation.loc[:,tag]
                    
            for index,item in enumerate(data_with_tag):
                if not pd.isnull(item):
                    
                    #对每一个字符串进行切片操作
                    item = str(item)
                    dataList = re.split(r'[;,&/|]', item) 
                    
                    #去除前后空格
                    for it in range(len(dataList)):
                        dataList[it] = dataList[it].strip()
                    
                    #重新拼接为合法字符串
                    pureDataString = ",".join(str(i) for i in dataList)
                    #填充操作
                    self.consolidation.loc[index,tag] = pureDataString
                    result.extend(dataList)
            #去重            
            result = list(set(result))
            
            #去除非法删除字符
            for dropItem in self.dropList:
                if dropItem in result:
                    result.remove(dropItem)
            
            #将结果填充至字典
            result_with_tag[tag] = result
        
        return result_with_tag

    # 导出数据 函数
    def exportData(self, dict_with_tag):
        for key in dict_with_tag:
            series_with_tag = pd.Series(dict_with_tag.get(key))
            series_with_tag.to_excel("./movie_extraction/"+key+".xlsx")
        
        

"""
# Main Program

dropList = ["Various",""," "]
tagList = ["movie_category","director","actor","main_actor"]
path = "movie_data_consolidation.xlsx"

# 加载数据
extraction = Extraction()
extraction.loadDataSource(path, dropList)

# 获得每段的数据,并处理更新回数据源
dict_with_tag = extraction.splitAndDropDulplication(tagList)

# 导出部分数据
extraction.exportData(dict_with_tag)

# 导出person数据
personList = dict_with_tag.get("director").copy()
personList.extend(dict_with_tag.get("actor"))
personList.extend(dict_with_tag.get("main_actor"))
personList = list(set(personList))
s_personList = pd.Series(personList)
s_personList.to_excel("person.xlsx")

# 导出pure数据
extraction.consolidation = extraction.consolidation.iloc[:,1:]
extraction.consolidation.to_excel("pure_movie_data.xlsx")
"""

