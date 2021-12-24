# -*- coding: utf-8 -*-
# coding: utf-8
import pandas as pd
import chardet 
import csv
import json
import os

class Consanguinity:
    def get_encoding(self, file):
        with open(file,'rb') as f:
            return chardet.detect(f.read())['encoding']

    def get_consanguinity_dict(self, read_file, write_file):
        consanguinity_dict = {} # 保存父子血缘关系的数组
        mid_dict = {} # 中间数组，将asin + nerasin与父节点的asin对应起来，结构为<father_asin,asin_set>，其中father_asin为从挑选出来作
        write_file.writeheader()
        count = 0
        for row in read_file:
            # 处理当前行所有asin，获得一个set
            row_set = set(row['near_asin'].split(','))
            row_set.add(row['asin'])
            row_set.discard('')

            # 算asin_set之间的交集，如果有交集就将其father_asin设置为同一个
            # 有交集时需要将两个的asin_set取并集重新放入mid_dict中
            if not mid_dict:
                mid_dict[row['asin']] = row_set
                consanguinity_dict[row['asin']]=row['asin']
            else:
                for key in list(mid_dict.keys()):
                    if set(mid_dict[key]).intersection(row_set):
                        consanguinity_dict[row['asin']] = key
                        # 可以优化为set(mid_dict[key].union(row_set))
                        for i in mid_dict[key]:
                            row_set.add(i)
                        mid_dict[key] = row_set
                        count+=1
                        break
                    else:
                        mid_dict[row['asin']] = row_set
                        consanguinity_dict[row['asin']]=row['asin']
        return consanguinity_dict

    def process_consanguinity(self, read_file, write_file):
        consanguinity_dict = self.get_consanguinity_dict(read_file,write_file)
        write_file.writeheader()
        for key,val in consanguinity_dict.items():
            write_file.writerow({'asin':key,'father_asin':val})

    # 获得<father_asin,count>数组，其中father_asin代表父asin，count代表该父asin所对应子节点数量
    def get_count_dict(self, file_name = './asin_relationship/consanguinity1.csv'):
        movie_data = csv.DictReader(open(file_name,'r'))
        next(movie_data)
        count_dict = {}
        for row in movie_data:
            if row['asin']!=row['father_asin']:
                if row['father_asin'] in count_dict:
                    count_dict[row['father_asin']] += 1
                else:
                    count_dict[row['father_asin']] = 1
        return count_dict

    def count_father_asin(self):
        count_dict = self.get_count_dict()
        write_file = csv.DictWriter(open('./asin_relationship/count_father_asin1.csv','w',newline=''),['father_asin','count'])
        write_file.writeheader()
        for key,val in count_dict.items():
            write_file.writerow({'father_asin':key,'count':val})

'''
if __name__ == '__main__':

    consanguinity = Consanguinity()
    movie_data = csv.DictReader(open('movie_data.csv','r',encoding= 'utf-8'))
    write_consanguinity = csv.DictWriter(open('./asin_relationship/consanguinity1.csv','w',newline='',encoding = 'utf-8'),['asin','father_asin'])

    # 获得血缘关系csv
    consanguinity.process_consanguinity(movie_data, write_consanguinity)
    # 获得每个父asin所对应的子asin数量
    consanguinity.count_father_asin()
'''