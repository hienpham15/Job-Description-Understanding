# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import pymongo
import sys
#from scrapy.conf import settings
#from scrapy import log

# =============================================================================
# class MongoDBPipeline(object):
#     def __init__(self):
#         connection = pymongo.MongoClient(settings['MONGODB_SERVER'],
#                                          settings['MONGODB_PORT'])
#         db = connection([settings['MONGODB_DB']])
#         self.collection = db[settings['MONGODB_COLLECTION']]
#         
#     def process_item(self, posting, spider):
#         # self.collection.update()
#         log.msg("Crawled 3 indeed pages for DE offers",
#                 level=log.DEBUG,
#                 spider=spider)
#         return posting
# =============================================================================

# =============================================================================
# class JobsPipeline:
#     def process_item(self, item, spider):
#         return item
# =============================================================================

class MongoDBPipeline:
    collection = 'jds_indeed'
    
    def __init__(self, mongodb_uri, mongodb_db):
        self.mongodb_uri = mongodb_uri
        self.mongodb_db = mongodb_db
        if not self.mongodb_uri:
            sys.exit("Connection String is required!")
            
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongodb_uri = crawler.settings.get('MONGODB_URI'),
            mongodb_db = crawler.settings.get('MONGODB_DATABASE', 'jobs')
        )
    
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongodb_uri)
        self.db = self.client[self.mongodb_db]
        
        # Start with a clean database
        self.db[self.collection].delete_many({})

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection].insert_one(dict(item))
        return item