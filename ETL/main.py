# -*- coding: utf-8 -*-
"""
Created on Fri Dec 24 17:30:11 2021

@author: 14218
"""
from comment_cleaning.comment_cleaning import CommentCleaning
from asin_relationship.asin_relationship import AsinRelationship
from comment_analysis.comment_sentiment_analysis import CommentSentimentAnalysis
from movie_data_cleaning.movie_data_cleaning import MovieDataCleaning
from movie_data_consolidation.movie_data_consolidation import MovieDataConsolidation
from movie_extraction.movie_extraction import Extraction
from movie_crawler.selenium import Spider
from asin_relationship.disjoint import Consanguinity
from movie_data_parse.DataParseManager import DataParseManager

import pandas as pd
import csv


class Test:
    
    def __init__(self):
        print("test init")
    
    def commentCleaningTest(self):
        print("*************清理评论集并分离评论数据 测试**************")
        a = CommentCleaning()
        a.loadAsinRelationship("./comment_cleaning/asin_relationship.xlsx")
        a.loadMovieAsin("./comment_cleaning/movie_data_cleaning.xlsx")
        a.deal("./comment_cleaning/movie_comments.json")
        a.splitComment()
        # a.printData(0)
        print("*********************测试完成*************************")
        
    def asinRelationshipTest(self):
        print("*************获得电影版本冲突关系 测试*****************")
        a = AsinRelationship()
        a.loadFile("./asin_relationship/res.json","./asin_relationship/movie_data.csv")
        a.getRelationship()
        a.printData("./asin_relationship/asin_relationship.csv","./asin_relationship/father_asin_count.csv")
        print("*********************测试完成*************************")
    
    def commentSentimentAnalysisTest(self):
        print("*************评论集情感分析 测试***********************")
        '''
        index = input("please input the comment file index: \n")
        index = int(index) 
        start = input("please input the start index of row: \n")
        start = int(start)
        
        c = CommentSentimentAnalysis(index,start)
        print("======== start to analysis comment data =========")
        c.analysisComment()
        '''
        print("由于调用外部接口需要上传相应的Key与Id，因此提供已调试完成的代码")
        print("*********************测试完成*************************")

    def movieDataCleaningTest(self):
        print("*************电影数据清洗 测试***********************")
        movieData = MovieDataCleaning("./movie_data_cleaning/movie_data.xlsx")

        #去除特殊符号值同样表示不存在这条列数据;
        movieData.removeSymbolValue()
        movieData.deal()
        movieData.printData("./movie_data_cleaning/movie_data_cleaning.xlsx")

        print("*********************测试完成*************************")
        
    def movieDataConsolidationTest(self):
        print("*************电影数据版本合并 测试***********************")
        c = MovieDataConsolidation("./movie_data_consolidation/movie_data_cleaning.xlsx")
        c.loadFile("./movie_data_consolidation/father_asin_count.csv", "./movie_data_consolidation/asin_relationship.csv")
        c.getAsinDict()
        c.solve()
        c.getDistinctData()
        c.printData("./movie_data_consolidation/movie_data_consolidation.xlsx")

        print("*********************测试完成*************************")        
        
    def movieExtractionTest(self):
        # Main Program
        print("*************电影数据抽取 测试***********************")
        dropList = ["Various",""," "]
        tagList = ["movie_category","director","actor","main_actor"]
        path = "./movie_extraction/movie_data_consolidation.xlsx"
        
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
        s_personList.to_excel("./movie_extraction/person.xlsx")
        
        # 导出pure数据
        extraction.consolidation = extraction.consolidation.iloc[:,1:]
        extraction.consolidation.to_excel("./movie_extraction/pure_movie_data.xlsx")
        print("*********************测试完成*************************") 
    
    def crawlerTest(self):
        print("*************电影数据爬取 测试***********************")
        #spider = Spider()
        print("需要引入相应包后, 进行环境变量配置后即可运行代码")
        print("*********************测试完成*************************") 
   
    def disjointTest(self):
        print("*************电影数据版本冲突关系 测试***********************")
        consanguinity = Consanguinity()
        movie_data = csv.DictReader(open('./asin_relationship/movie_data.csv','r',encoding= 'utf-8'))
        write_consanguinity = csv.DictWriter(open('./asin_relationship/consanguinity1.csv','w',newline='',encoding = 'utf-8'),['asin','father_asin'])
    
        # 获得血缘关系csv
        consanguinity.process_consanguinity(movie_data, write_consanguinity)
        # 获得每个父asin所对应的子asin数量
        consanguinity.count_father_asin()        
        print("*********************测试完成*************************") 
        
    def dataParseTest(self):
        # 测试
        print("*************电影数据提取 测试***********************")
        dataParseManager = DataParseManager("./movie_data_parse/data")
        dataParseManager.manage_data_to_csv("./movie_data_parse/outputTest")
        print("*********************测试完成*************************")
        
    def testAll(self):
        self.crawlerTest()
        
        self.dataParseTest()
        
        self.disjointTest()
        self.asinRelationshipTest()
        
        self.movieDataCleaningTest()
        
        self.movieDataConsolidationTest()
        
        self.movieExtractionTest()
        
        self.commentCleaningTest()
        
        self.commentSentimentAnalysisTest()
        
if __name__ == "__main__":
    # 测试
    test = Test()
    test.testAll()