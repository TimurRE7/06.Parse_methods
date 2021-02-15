# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


# class GbParseItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass


# class AutoyoulaItem(scrapy.Item):
#     _id = scrapy.Field()
#     title = scrapy.Field()
#     images = scrapy.Field()
#     description = scrapy.Field()
#     url = scrapy.Field()
#     author = scrapy.Field()
#     specifications = scrapy.Field()
#     price = scrapy.Field()
#     test = scrapy.Field()


class HHVacancyItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    company_url = scrapy.Field()
    company_name = scrapy.Field()
    company_site = scrapy.Field()
    company_sphere = scrapy.Field()
    company_description = scrapy.Field()


class Inst(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    img = scrapy.Field()


class InstTag(Inst):
    pass


class InstPost(Inst):
    pass
