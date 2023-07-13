# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import pymongo
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from itemadapter import ItemAdapter


class GbParsePipeline:
    def process_item(self, item, spider):
        return item


class MongoSavePipeline:

    def __init__(self):
        self.db_client = pymongo.MongoClient(os.getenv('DATA_BASE'))

    def process_item(self, item, spider):
        db = self.db_client['instagram']
        collection = db[type(item).__name__]
        collection.insert_one(item)
        return item


# class GbImagePipeline(ImagesPipeline):
#     def get_media_requests(self, item, info):
#         try:
#             img_url = item['data']['display_url']
#         except KeyError:
#             img_url = item['data']['profile_pic_url']
#         except:
#             img_url = []
#         yield Request(img_url)
#
#     def item_completed(self, results, item, info):
#         print(1)
#         item['data']['display_url'] = [itm[1] for itm in results]
#         return item

# class GbImagePipeline(ImagesPipeline):
#     def get_media_requests(self, item, info):
#         img_url_data = item['data']
#         try:
#             img_url = img_url_data['profile_pic_url_hd']
#         except KeyError:
#             img_url = img_url_data['profile_pic_url']
#         except:
#             img_url = []
#         yield Request(img_url)
#
#     def item_completed(self, results, item, info):
#         item['data']['profile_pic_url_hd'] = [itm[1] for itm in results]
#         return item
