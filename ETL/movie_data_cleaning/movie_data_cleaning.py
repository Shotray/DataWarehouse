#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   movie_data_cleaning_consolidation.py
@Contact :   1421877537@qq.com
@License :   (C)Copyright 2017-2018
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2021/11/30 14:31    leoy        1.0        a python file to deal the movie de...
"""

# import lib

import pandas as pd
import re

'''
asin | movie_title | movie_edition | movie_format | movie_score | director 
| main_actor | actor | movie_category | movie_release_date | near_asin | comment_num | db_raring_score

'''

class MovieDataCleaning:
    
    def __init__(self, dataPath):
        
        self.data = pd.read_excel(dataPath)
    
    # 去除所有换行符
    # 数据清洗/对每一列的非法值或者空值进行处理   
    def removeNewLine(self, attribute):
        self.data[attribute] = self.data[attribute].apply(lambda x: x.strip())
        self.data[attribute] = self.data[attribute].apply(lambda x: x.replace("\n",""))
        self.data[attribute] = self.data[attribute].apply(lambda x: x.replace("'\n",""))
        self.data[attribute] = self.data[attribute].apply(lambda x: x.replace("\r",""))
        self.data[attribute] = self.data[attribute].apply(lambda x: x.replace('"',"'"))
        self.data[attribute] = self.data[attribute].apply(lambda x: x.replace('“',"'"))
        self.data[attribute] = self.data[attribute].apply(lambda x: x.replace('‘',"'"))
        self.data[attribute] = self.data[attribute].apply(lambda x: x.replace('’',"'"))
        self.data[attribute] = self.data[attribute].apply(lambda x: x.replace('”',"'"))
    
    def removeSymbolValue(self):
        naList = [',',' ','-','_','.','*',"None","N/a","N/A","na","[]","__","~","none","nan","|"]
        
        for column in ('movie_title','director','actor','main_actor','movie_category'):
            self.data.loc[self.data[column].isin(naList),column] = ""
        
        for column in ('director','actor','main_actor'):
            self.data.loc[self.data[column].str.lower().str.contains('various',na=False),column] = ""
        
        self.data = self.data.astype({"movie_title":"str","movie_score":"float","director":"str",
                    "main_actor":"str","actor":"str", "movie_category":"str"})
        
        
    def removeBrackets(self, attribute):
        #去除掉一个字符串的括号及括号内的内容
        self.data[attribute] = self.data[attribute].apply(lambda x: re.sub('\(.*?\)','',x))
        #去除掉一个字符串的[]括号
        self.data[attribute] = self.data[attribute].apply(lambda x: re.sub('\[.*?\]','',x))
        #去除字符串以(结尾的内容
        self.data[attribute] = self.data[attribute].apply(lambda x: re.sub('(\(.*?)$','',x))
        #去除字符串以)结尾的内容
        self.data[attribute] = self.data[attribute].apply(lambda x: re.sub('(\).*?)$','',x))
    
    def dealMovieTitle(self):
        # movie_title
        self.data['movie_title'] = self.data['movie_title'].fillna("")    
        self.removeNewLine('movie_title')
        self.removeBrackets('movie_title')
    
    def dealMovieEdition(self):
        # movie_edition
        # 清洗空值
        self.data['movie_edition'] = self.data['movie_edition'].fillna("")
        self.removeNewLine('movie_edition')
        
    def dealMovieFormat(self):
        # movie_format
        self.data['movie_format'] = self.data['movie_format'].fillna("")
        self.removeNewLine('movie_format')
        self.removeBrackets('movie_format')
        
    def dealMovieScore(self):
        # movie_score
        # 标识为-1表示为不参与平均score的计算过程
        self.data['movie_score'] = self.data['movie_score'].fillna(-1)

    def dealDirector(self):
        # director
        self.data['director'] = self.data['director'].fillna("")
        self.removeNewLine('director')
        self.removeBrackets('director')
        
    def dealMainActor(self):
        # main_actor
        self.data['main_actor'] = self.data['main_actor'].fillna("")
        self.removeNewLine('main_actor')
        self.removeBrackets('main_actor')
    
    def dealActor(self):
        # actor
        self.data['actor'] = self.data['actor'].fillna("")
        self.removeNewLine('actor')
        self.removeBrackets('actor')
        
    def dealMovieCategory(self):
        # movie_category
        self.data['movie_category'] = self.data['movie_category'].fillna("")
        self.removeNewLine('movie_category')
        self.removeBrackets('movie_category')
        
    def dealMovieReleaseDate(self):
        # movie_release_date
        self.data['movie_release_date'] = self.data['movie_release_date'].fillna("")
    
    def dealNearAsin(self):
        
        # near_asin
        self.data['near_asin'] = self.data['near_asin'].fillna("")
        self.removeNewLine('near_asin')
        self.data['near_asin'] = self.data['near_asin'].apply(lambda x: x.replace('"',''))
        
    def dealCommentNum(self):
        # comment_num
        self.data['comment_num'] = self.data['comment_num'].fillna(0)
        
    def dealDbRaringScore(self):
        # db_raring_score
        # 同样表示不记录
        self.data['db_raring_score'] = self.data['db_raring_score'].fillna(-1)
        
    def fillActorAndMainActor(self):
        # 由于演员与主演关系比较特别，选择两者之间有一个为空时，用另一个替代
        for index,row in self.data.iterrows():
            if row['actor'] == "" and row['main_actor'] != "":
                self.data.loc[index,'actor'] = self.data.loc[index,'main_actor']
            elif row['actor'] != "" and row['main_actor'] == "":
                self.data.loc[index,'main_actor'] = self.data.loc[index,'actor']
    
    def deal(self):
        self.dealActor()
        self.dealCommentNum()
        self.dealDbRaringScore()
        self.dealDirector()
        self.dealMainActor()
        self.dealMovieCategory()
        self.dealMovieEdition()
        self.dealMovieFormat()
        self.dealMovieReleaseDate()
        self.dealMovieScore()
        self.dealMovieTitle()
        self.dealNearAsin()
        self.fillActorAndMainActor()
        
    def printData(self, path):
        self.data.to_excel(path)
    
"""    
#Main Program

movieData = MovieDataCleaning("movie_data.xlsx")

#去除特殊符号值同样表示不存在这条列数据;
movieData.removeSymbolValue()
movieData.deal()
movieData.printData("movie_data_cleaning.xlsx")
"""








 







































