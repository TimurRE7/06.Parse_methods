# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GbParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AutoyoulaItem(scrapy.Item):
    title = scrapy.Field()
    images = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    author = scrapy.Field()
    specifications = scrapy.Field()
    price = scrapy.Field()
