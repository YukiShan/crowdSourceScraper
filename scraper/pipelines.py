# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
import errno
from scrapy.exporters import JsonLinesItemExporter
from scrapy.exporters import CsvItemExporter
from os import path
import os
from scrapy.exceptions import DropItem
import pymongo
from scrapy.conf import settings 

import scrapy
import logging

class InstantJsonExportPipeline(object):
    def __init__(self):
        self.xporters = {}

    def process_item(self, item, spider):
        """
        Writes the item to output
        """

        # create the output file for a new class of item per spider
        settings = spider.crawler.settings
        if item.__class__ not in self.xporters[spider.name]:
            filename = '%s-%s.json' % (item.export_filename, settings['CRAWL_TS'])
            dirpath = path.join(settings.get('IO_PATH', 'io'), spider.name)
            _mkdir_p(dirpath)
            file_h = open(path.join(dirpath, filename), 'w')
            xporter = JsonLinesItemExporter(file=file_h)
            xporter.start_exporting()
            self.xporters[spider.name][item.__class__] = (file_h, xporter)

        xporter = self.xporters[spider.name][item.__class__][1]
        xporter.export_item(item)
        return item

    def open_spider(self, spider):
        self.xporters[spider.name] = {}

    def close_spider(self, spider):
        """
        Finishes writing
        """

        for file_h, xporter in self.xporters[spider.name].values():
            xporter.finish_exporting()
            file_h.close()


def _mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

class InstantCSVExportPipeline(object):
    def __init__(self):
        self.xporters = {}

    def process_item(self, item, spider):
        """
        Writes the item to output
        """

        # create the output file for a new class of item per spider
        settings = spider.crawler.settings
        if item.__class__ not in self.xporters[spider.name]:
            filename = '%s.csv' % item.export_filename
            dirpath = path.join(settings.get('IO_PATH', 'io'), settings['DATA_SET'])
            _mkdir_p(dirpath)
            file_h = open(path.join(dirpath, filename), 'w')
            xporter = CsvItemExporter(file=file_h)
            xporter.start_exporting()
            self.xporters[spider.name][item.__class__] = (file_h, xporter)

        xporter = self.xporters[spider.name][item.__class__][1]
        xporter.export_item(item)
        return item

    def open_spider(self, spider):
        self.xporters[spider.name] = {}

    def close_spider(self, spider):
        """
        Finishes writing
        """

        for file_h, xporter in self.xporters[spider.name].values():
            xporter.finish_exporting()
            file_h.close()


class DuplicatesPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item.export_filename != 'seed': 
            return
            
        itm_id = (item.export_filename, item.key)
        if itm_id in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % str(itm_id))
        else:
            self.ids_seen.add(itm_id)
            return item


class MongoDBPipeline(object):
    def __init__(self):
        connectAmzn = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
            ) 

        connectionAPP = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
            ) 

        db_amzn = connectAmzn[settings['MONGODB_AMZN_TASK_DB']]
        self.connectAmzn = db_amzn[settings['MONGODB_AMZN_TASK_COLLECTION']]        

        db_app = connectionAPP[settings['MONGODB_APP_TASK_DB']]
        self.connectionAPP = db_app[settings['MONGODB_APP_TASK_COLLECTION']] 

    def process_item(self, item, spider):
        """
        Writes the item to a database
        """
        connection = pymongo.MongoClient('localhost',27017);
        if item.export_filename == 'seed':            
            db_amzn = connection[settings['MONGODB_AMZN_TASK_DB']]
            # # print(">>>>>>>>>>>>>44444444")
            # # print(db)
            # sth = db['amznSpamTasks']
            # # print(">>>>>>>>>>>>>3333333333")
            # # print(sth)    
            # other = sth.find_one({"amazonId":"B00TYSLOG2"})
            # print(">>>>>>>>>>>>>5555555555555")
            # print(other)
            if db_amzn['amznSpamTasks'].find_one({'id':item['id']}):
                # self.connectAmzn.update({'id': item['id']}, dict(item), upsert=True)
                return
            else:
                if not db_amzn['amznSpamTasks'].find_one({'amazonId':item['amazonId']}):
                 # print(">>>>>>>>>>>>>5555555555555")
                    self.connectAmzn.insert(dict(item))
             
            # self.logger.debug("Products' info added to MongoDB database!")
            return item
        else:
            db_app = connection[settings['MONGODB_APP_TASK_DB']]
            if db_app['appPaidTasks'].find_one({'id':item['id']}) and db_app['appPaidTasks'].find_one({'app_id':item['app_id']}):
                # self.logger.info("Duplicate item found: %s" % str(item['id']))
                # self.connectionAPP.update({'id': item['id']}, dict(item), upsert=True)
                return
            else:
                self.connectionAPP.insert(dict(item))                 
                # self.logger.debug("Products' info added to MongoDB database!")
            return item
