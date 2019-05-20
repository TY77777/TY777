# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PaperAllItem(scrapy.Item):
    source = scrapy.Field()
    content = scrapy.Field()
    public_time = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    crawl_time = scrapy.Field()
    html_size = scrapy.Field()
