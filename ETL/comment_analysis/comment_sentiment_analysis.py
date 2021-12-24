# -*- coding: utf-8 -*-
"""
Comment sentiment analysis

@author: leoy

"""
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.nlp.v20190408 import nlp_client, models
import pandas as pd
import csv
import re

class CommentSentimentAnalysis:
    
    def __init__(self, curIndex = 0, startIndex = 0):
        
        # 当前处理的comment次序 对应commentInfo的次序
        self.commentIndex = curIndex
        
        # 处理的起始位置
        self.startIndex = startIndex
        
        # 当前处理的comment数据
        self.commentDataFrame = pd.DataFrame()
        
        # 当前的Id,与密码
        self.secrets = self.readSecretPwd("pwd.txt")
        
        # 情感分析结果
        # asin值 电影名称 正向评价比例 负向评价比例 中性评价比例 总体分类结果
        self.analysisResult = []
        
        #writer
        self.write_file = open("./comment_result/analysisResult_"+str(self.commentIndex)+".csv", "a",newline="")
        self.writer = csv.DictWriter(self.write_file,["asin","Positive","Neutral","Negative","Sentiment"])
        if startIndex == 0:            
            self.writer.writeheader()
        #读取评论信息
        self.readCommentInfo()
        
        #初始化
        self.initClient()

    def readSecretPwd(self, path):
        '''

        Parameters
        ----------
        path : str
            获得Id,Key的路径.

        Returns
        -------
        secrets : dict
            Id,key的字典.

        '''
        secrets = {}
        file = open(path,"r",encoding = 'utf-8')
        curIndex = 0
        
        while 1:
            line = file.readline()
            if not line:
              break
            line = line.strip()
            lineList = line.split("\t")
            secrets[curIndex] = lineList
            curIndex += 1
        
        return secrets 


    def readCommentInfo(self):
    
        fileName = r"./comment/commentInfo_"+str(self.commentIndex)+".xlsx"
        self.commentDataFrame = pd.read_excel(fileName)
        self.commentDataFrame = self.commentDataFrame.loc[:,['asin','reviewText']]
        self.commentDataFrame.loc[:,"reviewText"].fillna("",inplace = True)
        for index in range(len(self.commentDataFrame)):
                
            self.commentDataFrame.loc[index,"reviewText"] = str(self.commentDataFrame.loc[index,"reviewText"]).replace('"',"'")
            self.commentDataFrame.loc[index,"reviewText"] = re.sub(r"^\s+$","",self.commentDataFrame.loc[index,"reviewText"])
        
    def initClient(self):
        
        i = self.commentIndex % len(self.secrets)
        secret = self.secrets.get(i)
        secretId = secret[0]
        secretKey = secret[1]
        
        cred = credential.Credential(secretId, secretKey)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "nlp.tencentcloudapi.com"
    
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        self.client = nlp_client.NlpClient(cred, "ap-guangzhou", clientProfile)
        self.req = models.SentimentAnalysisRequest()

    def analysis(self,text):
        
        try:
            result = {}
            params = {
                "Text": text,
                "Flag": 1,
                "Mode": "3class"
            }
            self.req.from_json_string(json.dumps(params))
        
            resp = self.client.SentimentAnalysis(self.req)
            
            resp = json.loads(resp.to_json_string())
            result["Positive"] = resp.get("Positive")
            result["Neutral"] = resp.get("Neutral")
            result["Negative"] = resp.get("Negative")
            result["Sentiment"] = resp.get("Sentiment")
            
            return result
                  
        except TencentCloudSDKException as err:
            print(text)
            print(err)
                
    def analysisComment(self):
        
        for index in range(self.startIndex,len(self.commentDataFrame)):
           
            if index % 1000 == 0:
                print(index)
            
            result = {}
            result['asin'] = str(self.commentDataFrame.loc[index,'asin'])
            text = self.commentDataFrame.loc[index,'reviewText']
            
            if pd.isnull(text) or str(text) == "" or len(str(text)) > 200 :
                continue
            
            r = self.analysis(text)
            
            self.writer.writerow(dict(result,**r))
            
"""
if __name__ == "__main__":    
    
    index = input("please input the comment file index: \n")
    index = int(index) 
    start = input("please input the start index of row: \n")
    start = int(start)
    
    c = CommentSentimentAnalysis(index,start)
    print("======== start to analysis comment data =========")
    c.analysisComment()
"""    
    
    
    
    
    
    
    
    
    
    
    
    
    