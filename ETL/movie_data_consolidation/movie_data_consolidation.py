# -*- coding: utf-8 -*-
"""
@File    :   movie_data_consolidation.py    
@Contact :   1421877537@qq.com
@License :   (C)Copyright 2017-2018
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2021/11/30 18:45    leoy        1.0         combine the different versions of the movie data...
"""

# import lib
import pandas as pd

class MovieDataConsolidation:
    def __init__(self,path):
        self.data = pd.read_excel(path)
        self.data = self.data.iloc[:,1:]
        self.fillnaFordata()
        
    def loadFile(self,fatherAsinPath,asinRelationshipPath):
        self.father_asin = pd.read_csv(fatherAsinPath)
        self.asin_relationship = pd.read_csv(asinRelationshipPath)
        self.asin_relationship_distinct = self.asin_relationship[self.asin_relationship['asin']!=self.asin_relationship['father_asin']]
        self.asin_relationship_distinct = self.asin_relationship_distinct.reset_index(drop = True)
    
        for index,row in self.asin_relationship_distinct.iterrows():
            if len(row['asin']) < 10 and row['asin'][0] <='9' and row['asin'][0] >= '1':
                self.asin_relationship_distinct.loc[index,'asin'] = '0'*(10-len(row['asin']))+row['asin']
        
            if len(row['father_asin']) < 10 and row['father_asin'][0] <'9' and row['father_asin'][0] > '1':
                self.asin_relationship_distinct.loc[index,'father_asin'] = '0'*(10-len(row['father_asin']))+row['father_asin']
            
    def getAsinDict(self):
        self.asinDict= {}
        for index,row in self.asin_relationship_distinct.iterrows():
            
            
            father_asin_value = row['father_asin']
            if father_asin_value not in self.asinDict:
                self.asinDict[father_asin_value] = [father_asin_value,row['asin']]
            else:
                self.asinDict.get(father_asin_value).append(row['asin'])
                        
            
    def fillnaFordata(self):
        for column in ('movie_title','director','main_actor','actor','movie_category'):
            self.data[column].fillna("",inplace = True)
        
    def getMovieTitle(self, sonList):
        minLengthTitle = ""
        minLength = 1000
        
        for index,asin in enumerate(sonList):
            cursor = self.data[self.data['asin'] == asin]
            cursor = cursor.loc[:,'movie_title']
    
            cursor_movie_title = cursor.iloc[0]
            
            if cursor_movie_title == "":
                continue
            
            if len(cursor_movie_title) < minLength:
                minLength = len(cursor_movie_title)
                minLengthTitle = cursor_movie_title
        
        return minLengthTitle
    
    def getMovieScoreAndCommentCount(self, sonList):
    
        comment_count = 0
        avg_score = 0
        
        for index,asin in enumerate(sonList):
            cursor = self.data[self.data['asin'] == asin]
            cursor = cursor.loc[:,['comment_num','movie_score']]
            
            comment_num = cursor.iloc[0,0]
            movie_score = cursor.iloc[0,1]
            
    
            if movie_score < 0 or comment_num == 0:
                continue
            comment_count += comment_num.astype(int)
            avg_score += movie_score.astype(float) * comment_num.astype(int)
        
        if comment_count != 0:
            avg_score /= comment_count
        
        return {'avg_score':avg_score,'comment_num':comment_count}
    
    
    def getDirector(self, sonList):
    
        result_director = ""
        director_num = 1000
        
        
        for index,asin in enumerate(sonList):
            
            cursor = self.data[self.data['asin'] == asin]
            cursor = cursor.loc[:,'director']
    
            director = cursor.iloc[0]
            
            if director == "":
                continue
            
            directorList = director.split(',')
            if len(directorList) < director_num:
                result_director = director
                director_num = len(directorList)
            
        return result_director
    
    def getActor(self, sonList):
    
        result_actor = ""
        actor_num = 0
        
        
        for index,asin in enumerate(sonList):
            
            cursor = self.data[self.data['asin'] == asin]
            cursor = cursor.loc[:,'actor']
    
            actor = cursor.iloc[0]
            
            if actor == "":
                continue
            
            actorList = actor.split(',')
            if len(actorList) > actor_num:
                result_actor = actor
                actor_num = len(actorList)
            
        return result_actor
    
    def getMainActor(self, sonList):
    
        result_main_actor = ""
        main_actor_num = 0
        
        
        for index,asin in enumerate(sonList):
            
            cursor = self.data[self.data['asin'] == asin]
            cursor = cursor.loc[:,'main_actor']
    
            main_actor = cursor.iloc[0]
            
            if main_actor == "":
                continue
            
            actorList = main_actor.split(',')
            if len(actorList) > main_actor_num:
                result_main_actor = main_actor
                main_actor_num = len(actorList)
            
        return result_main_actor
    
    
    def getMovieReleaseDate(self, sonList):
        result_date = ""
        
        for index,asin in enumerate(sonList):
            cursor = self.data[self.data['asin'] == asin]
            cursor = cursor.loc[:,'movie_release_date']
            
            date = cursor.iloc[0]
            
            if pd.isnull(date):
                continue
            
            if result_date == "":
                result_date = date
            else:
                if result_date > date:
                    result_date = date
        
        return result_date
    
    def solve(self):
        
        for key in self.asinDict:
    
            movie_title = self.getMovieTitle(self.asinDict[key])
            result = self.getMovieScoreAndCommentCount(self.asinDict[key])
            movie_score = result.get('avg_score')
            comment_num = result.get('comment_num')
            director = self.getDirector(self.asinDict[key])
            actor = self.getActor(self.asinDict[key])
            main_actor = self.getMainActor(self.asinDict[key])
            date = self.getMovieReleaseDate(self.asinDict[key])
            
            # 获得版本对比之间的综合数据
            self.data.loc[self.data['asin'] == key,'movie_title'] = movie_title
            self.data.loc[self.data['asin'] == key,'movie_score'] = movie_score
            self.data.loc[self.data['asin'] == key,'comment_num'] = comment_num
            self.data.loc[self.data['asin'] == key,'director'] = director
            self.data.loc[self.data['asin'] == key,'actor'] = actor
            self.data.loc[self.data['asin'] == key,'main_actor'] = main_actor
            self.data.loc[self.data['asin'] == key,'movie_release_date'] = date
    
    def getDistinctData(self):
        drop_list = self.asin_relationship_distinct['asin'].tolist()
        self.data_del = self.data[~self.data['asin'].isin(drop_list)]
        self.data_del = self.data_del.reset_index(drop = True)
        
        
        # 添加asinCount字段 删除nearAsin字段
        self.data_del['asin_count'] = 1
        self.data_del.drop(columns=['near_asin'],inplace=True)
        
        father_set = self.father_asin.loc[:,'father_asin'].to_list()
        asin_set = self.data_del.loc[:,"asin"].to_list()
        for f_asin in father_set:
            if f_asin in asin_set:
                self.data_del.loc[self.data_del['asin'] == f_asin,'asin_count'] = self.father_asin.loc[self.father_asin["father_asin"] == f_asin,"count"].values[0]
    

    def printData(self,path):
        self.data_del.to_excel(path)
    
"""
c = MovieDataConsolidation("movie_data_cleaning.xlsx")
c.loadFile("father_asin_count.csv", "asin_relationship.csv")
c.getAsinDict()
c.solve()
c.getDistinctData()
c.printData("movie_data_consolidation.xlsx")
 """   
    
    
    
    
    
    
    
    
    
    
    
    