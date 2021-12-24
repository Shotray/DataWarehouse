# coding:utf-8
from lxml import etree
import os
import re
import threading
import csv

class DataParseManager:
    def __init__(self, filePath):
        self.filePath = filePath
        # 依次读入文件夹内的所有txt
        self.files = os.listdir(filePath)

    # 使用xpath进行数据解析
    def parseData(self,start_index, end_index, t, writer):
        for i in range(start_index, end_index):
            html_selector = etree.parse(self.filePath + "/" + self.files[i], etree.HTMLParser())
            print('当前解析的文件:', self.files[i], i, "thread:", t)
            # 提取title
            movie_title = html_selector.xpath('normalize-space(//span[@id="productTitle"]/text())')
            # 提取电影类型
            movie_category = html_selector.xpath('//a[@class="a-link-normal a-color-tertiary"][last()]/text()')
            # 电影主演列表
            main_actor_list = []
            # 电影导演列表
            director_list = []
            # 获取的所有演职员信息列表
            actor_director_info = html_selector.xpath(
                '//span[@class="author notFaded"]/a[@class="a-link-normal"]/text()')

            more_actor_info = html_selector.xpath('//span[@class="author"]/a[@class="a-link-normal"]/text()')
            actor_director_info = actor_director_info + more_actor_info

            # 获取到的所有演职员类型信息列表
            actor_director_category_info = html_selector.xpath('//span[@class="contribution"]/span/text()')
            # 获取到的格式信息
            movie_format = html_selector.xpath('//div[@id="bylineInfo"]/span/text()')
            if len(movie_format) != 0:
                movie_format = movie_format[-1]

            # 获取电影的评分
            movie_score = html_selector.xpath('//span[@class="a-size-medium a-color-base"]/text()')
            if len(movie_score) != 0:
                movie_score = movie_score[0]
                movie_score = movie_score[0:movie_score.rfind('，')]
                movie_score = re.findall(r"\d+\.?\d*", movie_score)
                movie_score = movie_score[0]

            # 获取电影的评论总数
            movie_comment_num = html_selector.xpath(
                '//a[@id="acrCustomerReviewLink"]//span[@class="a-size-base"]/text()')
            if len(movie_comment_num) != 0:
                movie_comment_num = re.findall(r"\d+\.?\d*", movie_comment_num[0])
                movie_comment_num = movie_comment_num[0]
            else:
                movie_comment_num = ""

            # 获取电影的near_asin
            movie_near_asin = html_selector.xpath('//li[@class="swatchElement unselected"]//a/@href')
            movie_near_asin_list = []
            # 获取url中的asin信息
            for asin in movie_near_asin:
                near_asin_start_pos = asin.rfind('dp') + 3
                near_asin_end_pos = asin.rfind('ref')
                new_str = asin[near_asin_start_pos:near_asin_end_pos][-11:-1]
                movie_near_asin_list.append(new_str)

            # 电影版本
            movie_edition = html_selector.xpath('//span[@id="editions"]/text()')

            director_list = set()
            # 处理演员信息和导演信息
            for index in range(len(actor_director_category_info)):
                if 'Actor' in actor_director_category_info[index]:
                    main_actor_list.append(actor_director_info[index])
                if 'Director' in actor_director_category_info[index] or 'Author' in actor_director_category_info[index]:
                    director_list.add(actor_director_info[index])

            # 电影主要信息
            movie_actor_list = ','.join(main_actor_list)
            movie_main_info = html_selector.xpath('//span[@class="a-list-item"]//span/text()')

            movie_release_date = ""
            for index in range(len(movie_main_info)):
                # 获取发布日期
                if movie_main_info[index].strip()[0:4] == "发布日期":
                    movie_release_date = movie_main_info[index + 1].strip()
                # 电影的演员列表
                if movie_main_info[index].strip()[0:2] == "演员":
                    movie_actor_list = movie_main_info[index + 1]
                    # print(movie_actor_list)
                if movie_main_info[index].strip()[0:2] == "导演":
                    new_list = movie_main_info[index + 1].strip().split(',')

                    for director in new_list:
                        director_list.add(director)
                if movie_main_info[index].strip()[0:4] == "ASIN":
                    asin = movie_main_info[index + 1].strip()
                if movie_main_info[index].strip()[0:4] == "电影风格":
                    movie_style = movie_main_info[index + 1].strip()

            # 若电影的发布日期为空
            if movie_release_date == "":
                new_li = html_selector.xpath(
                    '//div[@class="top-level selected-row"]//span[@class="a-size-small a-color-base"]/text()')
                for ele in new_li:
                    if '年' in ele:
                        movie_release_date = ele

            asin = self.files[i][0:self.files[i].rfind('.')]
            if len(movie_category) != 0:
                movie_category = movie_category[-1].strip()

            director_list = set(director_list)

            # 新增电影的豆瓣评分
            db_rating_score = html_selector.xpath('//span[@class="imdb-rating"]/strong/text()')
            if len(db_rating_score) != 0:
                db_rating_score = db_rating_score[0]
            else:
                db_rating_score = ""

            if not ("TV" in movie_category or "Television" in movie_category or "电视" in movie_category):
                writer.writerow([asin, movie_title, ','.join(movie_edition), movie_format, movie_score,
                                 ','.join(director_list), ','.join(main_actor_list),
                                 movie_actor_list,
                                 movie_category, str(movie_release_date), ','.join(movie_near_asin_list),
                                 movie_comment_num,
                                 db_rating_score])

    # 指定要输出的文件的文件名，进行数据解析
    def manage_data_to_csv(self, outPutFileName):
        with open(outPutFileName+".csv", "w", newline='', encoding='utf-8') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(["asin", "movie_title", "movie_edition", "movie_format", "movie_score",
                             "director", "main_actor", "actor", "movie_category", "movie_release_date",
                             "near_asin", "comment_num", "db_raring_score"])
            threads = []
            num = int(len(self.files)/8)
            if num == 0:
                self.parseData(0, len(self.files),0,writer)
            else:
                for t in range(0, 8):
                    if t < 7:
                        t = threading.Thread(target=self.parseData, args=(t * num, (t + 1) * num, t, writer))
                    else:
                        t = threading.Thread(target=self.parseData, args=((t + 1) * num, len(self.files), t, writer))
                    threads.append(t)
                for thr in threads:
                    thr.start()
                for thr in threads:
                    thr.join()

"""
if __name__ == "__main__":
    # 测试
    dataParseManager = DataParseManager('E:/大三上/数据仓库/Xpath提取/test')
    dataParseManager.manage_data_to_csv("outputTest")
"""