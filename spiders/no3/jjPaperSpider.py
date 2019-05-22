#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   jjPaperSpider.py
@time:  2019-05-22 8:54 
@function:  21世纪经济报道数字报新闻爬虫
"""
import datetime
import random
import re
import sys
import time
import scrapy
from paper_all.items import PaperAllItem
from paper_all.spiders.util import spiderUtil


class jjNews(scrapy.Spider):
    name = "jjPaperSpider"
    start_url = "http://epaper.21jingji.com/"
    header = spiderUtil.header_util()

    def start_requests(self):
            yield scrapy.Request(url=self.start_url, callback=self.parse_item_list, headers=self.header)

    def parse_item_list(self, response):
        news_list = response.xpath("//div[@class='main']/ul/li/a/@href").extract()
        for news in news_list:
            yield scrapy.Request(url=news, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})", response.text).group(0) + ":00"
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@class='txtContent']//text()").extract()
                content = "".join(content_arr).strip()
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://epaper.21jingji.com/"

            try:
                author_arr = response.xpath("//div[@class='newsInfo']//text()").extract()
                author = "".join(author_arr).split(" ")[1].strip()
                if author == "":
                    author = "21世纪经济报道数字报"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title_arr1 = response.xpath("//div[@class='titleHead']/h1//text()").extract()
                title = "".join(title_arr1).strip()
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