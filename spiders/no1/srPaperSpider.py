#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   srPaperSpider.py
@time:  2019-05-15 
@function:  上饶日报新闻爬虫
"""
import datetime
import random
import re
import sys
import time
import scrapy
from paper_all.items import PaperAllItem
from paper_all.spiders.util import spiderUtil


class srNews(scrapy.Spider):
    name = "srPaperSpider"
    start_url = "http://paper.srxww.com/srrb/html/%s-%s/%s/node_2.htm"
    header = spiderUtil.header_util()

    def start_requests(self):
        list = []
        begin_date = datetime.datetime.strptime("2003-08-16", "%Y-%m-%d")
        end_date = datetime.datetime.strptime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
        while begin_date <= end_date:
            date_str = begin_date.strftime("%Y-%m-%d")
            list.append(date_str)
            begin_date += datetime.timedelta(days=1)
        for date in list:
            data_info = date.split("-")
            year = data_info[0]
            month = data_info[1]
            day = data_info[2]
            url = self.start_url % (year, month, day)
            time.sleep(1)
            yield scrapy.Request(url=url, callback=self.parse_item_home, headers=self.header)

    def parse_item_home(self, response):
        paper_list = response.xpath("//td[@class='default']/a[@id='pageLink']/@href").extract()
        for paper in paper_list:
            paper_url = response.url.split("node")[0] + paper
            yield scrapy.Request(url=paper_url, callback=self.parse_item_list, headers=self.header, dont_filter=True)

    def parse_item_list(self, response):
        news_list = response.xpath("//td[@class='default']/a/@href").extract()
        for news in news_list:
            if news.startswith("content"):
                news_url = response.url.split("node")[0] + news
                yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                public_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", response.text).group(0) + " 00:00:00"
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@id='ozoom']/founder-content/p/text()").extract()
                content = "".join(content_arr).strip()
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://paper.srxww.com/"

            try:
                author = "上饶日报"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title = response.xpath("//td[@class='font01']/text()").extract()[0]
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
