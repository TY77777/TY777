#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   bjPaperSpider.py
@time:  2019-05-15 
@function:  北京商报新闻爬虫
"""
import datetime
import json
import random
import re
import sys
import time
import scrapy
from paper_all.items import PaperAllItem
from paper_all.spiders.util import spiderUtil


class bjsbNews(scrapy.Spider):
    name = "bjPaperSpider"
    start_url = "http://api.bbtnews.com.cn/v1/index.php?controller=home&action=get_list&page=%s&size=22"
    header = spiderUtil.header_util()

    def start_requests(self):
        for page in range(1, 11605):
            url = self.start_url % page
            time.sleep(random.uniform(1,3))
            yield scrapy.Request(url=url, callback=self.parse_item_list, headers=self.header)

    def parse_item_list(self, response):
        load = json.loads(response.text)
        for data in load["data"]:
            news_url = data["url"]
            timeArray = time.localtime(int(data["published"]))
            public_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            author = data["author"]
            time.sleep(random.uniform(1,3))
            yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header,
                                 meta={"public_time": public_time, "author": author})

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                public_time = response.meta["public_time"]
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@id='pageContent']//text()").extract()
                content = "".join(content_arr).strip()
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.bbtnews.com.cn/"

            try:
                author = response.meta["author"]
                if author == "":
                    author = "北京商报"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title = response.xpath("//div[@class='article-hd']/h3/text()").extract()[0].strip()
            except:
                spiderUtil.log_level(6, response.url)

            try:
                #  and public_time.startswith(spiderUtil.get_first_hour()):
                if len(content) > 50:
                    item = PaperAllItem()
                    item["source"] = source
                    item["content"] = content
                    item["public_time"] = public_time
                    item["url"] = response.url
                    item["title"] = title
                    item["author"] = author
                    item["crawl_time"] = spiderUtil.get_time()
                    item["html_size"] = html_size
                    # print(item)
                    yield item
            except:
                pass
        else:
            spiderUtil.log_level(response.status, response.url)
