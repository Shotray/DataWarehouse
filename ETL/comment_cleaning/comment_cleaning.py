# -*- coding: utf-8 -*-
"""
@File    :   comment_cleaning.py
@Contact :   1421877537@qq.com
@License :   (C)Copyright 2017-2018
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2021/11/30 14:31    leoy        1.0      clean the comment data...
"""


#import lib
import pandas as pd
import json

class CommentCleaning:
    
    def __init__(self):
        self.data = []
        
    def loadAsinRelationship(self, path):
        
        '''
         获得需要替换为father_asin的asin信息
        '''
        asin_relationship = pd.read_excel(path)
        
        self.asin_relationship_distinct = asin_relationship[asin_relationship['asin']!=asin_relationship['father_asin']]
        self.asin_relationship_distinct = self.asin_relationship_distinct.reset_index(drop = True)
        
        # 长度不足的情况需要补足前面的零
        for index,row in self.asin_relationship_distinct.iterrows():
            if len(row['asin']) < 10 and row['asin'][0] <='9' and row['asin'][0] >= '1':
                self.asin_relationship_distinct.loc[index,'asin'] = '0'*(10-len(row['asin']))+row['asin']
        
            if len(row['father_asin']) < 10 and row['father_asin'][0] <'9' and row['father_asin'][0] > '1':
                self.asin_relationship_distinct.loc[index,'father_asin'] = '0'*(10-len(row['father_asin']))+row['father_asin']
        
        self.convert_asin_list = self.asin_relationship_distinct.loc[:,'asin'].to_list()  
        
    def loadMovieAsin(self,path):
        '''
         获得全部的movie的asin的信息
        '''
        asin_list = pd.read_excel(path)
        asin_list = asin_list.loc[:,'asin']
        asin_list.drop_duplicates(inplace = True)
        asin_list = asin_list.reset_index(drop = True)
        for index,item in enumerate(asin_list):
            if len(asin_list.iloc[index]) < 10 and asin_list.iloc[index] <='9' and asin_list.iloc[index] >= '1':
                asin_list.iloc[index] = '0'*(10-len(asin_list.iloc[index]))+asin_list.iloc[index]
        
        self.all_asin_list = asin_list.to_list()
        
        
    def deal(self, readerPath):
        # 声明一个存储comment信息的列表
        self.commentList = []
        
        # 按行读取文件
        commentReader = open(readerPath,"r")
        
        # 循环读取movie_comment.json文件,然后处理
        while True:
            line = commentReader.readline()
            if not line:
                break
        
            comment_json = json.loads(line)
            pending_asin = comment_json.get("asin")
            
            #获得asin进行判断
            if pending_asin in self.all_asin_list:
                
                if pending_asin in self.convert_asin_list:
                
                #需要转换的内容
                    father_asin = self.asin_relationship_distinct.loc[self.asin_relationship_distinct['asin'] == pending_asin,"father_asin"] 
                    if not father_asin.empty:
                        father_asin = father_asin.iloc[0]
                        comment_json["asin"] = father_asin
        
                self.commentList.append(comment_json)
        
    def splitComment(self):
        df_comment = pd.DataFrame(self.commentList)
        df_comment = df_comment.iloc[:,:-1]
        
        l = len(self.commentList)
        start = 0
        size = 500000
        self.df_comments = []
        current = start+size
        while current <= l:
            self.df_comments.append(df_comment.iloc[start:current,:])
            start = current
            current = current + size
        self.df_comments.append(df_comment.iloc[start:,:])
        
    def printData(self,index):
        if index < len(self.df_comments) - 1:
            self.df_comments[index].to_excel("commentInfo_"+str(index)+".xlsx")
        else:
            print("index out of the range.")
        
"""
a = CommentCleaning()
a.loadAsinRelationship("asin_relationship.xlsx")
a.loadMovieAsin("movie_data_cleaning.xlsx")
a.deal("movie_comments.json")
a.splitComment()
# a.printData(0)
"""        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        