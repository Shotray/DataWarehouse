from selenium.webdriver import Chrome
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
from amazoncaptcha import AmazonCaptcha
import random
import pandas as pd


class Spider:

    asinSet = None
    index = 0
    curParseCount = 0

    # 存储文件地点
    saveFileUrl='./movie_crawler'

    # 爬取的起点和终点
    startIndex=0
    endIndex=0

    def getNextUrl(self):
        # 寻找下一个可爬取的url
        while self.asinSet.iloc[self.index].hasDeal and self.index < self.endIndex:
            self.index += 1

        # 爬取结束
        if self.index >= self.asinSet.shape[0]:
            print('====全部数据集成功获取====')
            return -1

        print("{0}:{1}".format(self.index,
                               self.asinSet.iloc[self.index].asinID))

        return 'https://www.amazon.com/-/zh/dp/'+self.asinSet.iloc[self.index].asinID

    def __init__(self):
        options = ChromeOptions()
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2,
            }
        }
        options.add_experimental_option('prefs', prefs)
        # options.add_argument("--headless")
        self.driver = Chrome(options=options)

        # 读取文件
        self.asinSet = pd.read_csv('./movie_crawler/asin.csv')
        
        self.index=self.startIndex
        if self.endIndex == 0:
            self.endIndex=self.asinSet.shape[0]
        
        self.nextUrl = self.getNextUrl()

        while self.nextUrl != -1:
            self.getNextPage()
            self.nextUrl = self.getNextUrl()
            # 每10次爬取存储一次csv文件
            self.curParseCount += 1
            if self.curParseCount >= 10:
                self.saveAsinSet()
                self.curParseCount = 0

    '''
    处理页面
    '''

    def getNextPage(self):
        self.wait = WebDriverWait(self.driver, 0.8, 0.5)
        # 访问该网站
        self.driver.get(self.nextUrl)
        time.sleep(random.random())
        # 标记为已提取
        self.asinSet.iloc[self.index, 1] = True
        self.total = self.driver.page_source
        try:
            title = self.driver.find_element_by_xpath(
                '//span[@id="productTitle"]')
            print(title.text.replace('\n', ''))
            with open(self.saveFileUrl+self.nextUrl[-10:]+'.txt', 'w', encoding='utf-8') as fp:
                fp.write(self.total)
        except:
            # 处理验证码
            self.handleCaptcha()
            

    '''
    处理验证码
    '''

    def handleCaptcha(self):
        try:
            self.total = self.driver.page_source
            soup = BeautifulSoup(self.total, features="lxml")
            src = soup.find(
                class_="a-row a-text-center").findChild(name="img").attrs["src"]
            captcha = AmazonCaptcha.fromlink(src)
            solution = captcha.solve(keep_logs=True)
            print(solution)
            # <div contenteditable="plaintext-only"><br></div>
            input_element = self.driver.find_element_by_id("captchacharacters")
            input_element.send_keys(solution)

            button = self.driver.find_element_by_xpath("//button")
            button.click()

            print("已解决验证码√")

            #再来一次
            self.asinSet.iloc[self.index, 1] = False
        except:
            #404
            return

    def saveAsinSet(self):
        print('====存储asinSet.csv====')
        self.asinSet.to_csv('./movie_crawler/asin.csv', index=False)

'''
def run():
    spider = Spider()


if __name__ == "__main__":
    run()
'''