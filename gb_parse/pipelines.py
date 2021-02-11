# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import pymongo
from itemadapter import ItemAdapter


class GbParsePipeline:
    def process_item(self, item, spider):
        return item


class MongoSavePipeline:

    def __init__(self):
        self.db_client = pymongo.MongoClient(os.getenv('DATA_BASE'))

    def process_item(self, item, spider):
        db = self.db_client['hhru']
        collection = db[spider.name]
        collection.insert_one(item)
        return item
