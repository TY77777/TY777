#!/usr/bin/env python 
# coding: utf-8 
"""
@author: TongYao
@file:   qhrbPaperSpider.py
@time:  2019-05-17 
@function:  日货日报新闻爬虫
"""
import random
import re
import sys
import time
import scrapy
from paper_all.items import PaperAllItem
from paper_all.spiders.util import spiderUtil


class qhNews(scrapy.Spider):
    name = "qhPaperSpider"
    start_url = "http://www.qhdb.com.cn/Newspaper/PageNavigate.aspx?nid=%s"
    header = spiderUtil.header_util()

    def start_requests(self):
        for date in range(15, 2553):
            url = self.start_url % date
            time.sleep(1)
            # 全量数据
            yield scrapy.Request(url=url, callback=self.parse_item_home, headers=self.header)
            # 增量数据
            # yield scrapy.Request(url=url, callback=self.parse_item_today, headers=self.header)

    # 增量数据拿到今天日报页面
    def parse_item_today(self, response):
        today_list = response.xpath("//tr/td/a/@href").extract()[-1]
        today_url = response.url.split("PageNavigate")[0] + today_list
        yield scrapy.Request(url=today_url, callback=self.parse_item_home, headers=self.header,
                             dont_filter=True)

    def parse_item_home(self, response):
        paper_list = response.xpath("//div/span[@class='float']/a/@href").extract()
        for paper in paper_list:
            paper_url = response.url.split("PageNavigate")[0] + paper
            yield scrapy.Request(url=paper_url, callback=self.parse_item_list, headers=self.header,
                                 dont_filter=True)

    def parse_item_list(self, response):
        news_list = response.xpath("//div[@class='p_l_bottom']/div/a/@href").extract()
        for news in news_list:
            news_url = response.url.split("PageNavigate")[0] + news
            yield scrapy.Request(url=news_url, callback=self.parse, headers=self.header)

    def parse(self, response):
        if response.status == 200:
            text = response.text
            html_size = sys.getsizeof(text)

            try:
                public_time = re.search(r"(\d{4}/\d{1,2}/\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})", response.text).group(
                    0).replace("/", "-")
            except:
                spiderUtil.log_level(8, response.url)

            try:
                content_arr = response.xpath("//div[@class='article_content']//text()").extract()
                content = "".join(content_arr).strip()
            except:
                spiderUtil.log_level(7, response.url)

            source = "http://www.qhdb.com.cn/"

            try:
                author_arr = response.xpath("//span[@id='sZuoZhe']/text()").extract()
                author = "".join(author_arr)
                if author == "":
                    author = "期货日报"
            except:
                spiderUtil.log_level(9, response.url)

            try:
                title = response.xpath("//div[@class='article_title']//text()").extract()[0].strip()
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
