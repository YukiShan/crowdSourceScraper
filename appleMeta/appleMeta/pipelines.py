# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.conf import settings 
import pymongo

import scrapy
import logging

class AppleMongoDBPipeline(object):
	def __init__(self):
		connectionMETA = pymongo.MongoClient(
			settings['MONGODB_SERVER'],
			settings['MONGODB_PORT']
			)
		
		db_meta = connectionMETA[settings['MONGODB_APP_META_DB']]		
		
		self.connectionMETA = db_meta[settings['MONGODB_APP_META_COLLECTION']]


	def process_item(self, item, spider):
		# connection = pymongo.MongoClient('localhost',27017)
		# db_app = connection[settings['MONGODB_APP_DETAIL_DB']]
		# self.connectionAPP.update({'id': item['id']}, dict(item), upsert=True)
		if item.export_filename == 'app':
			self.connectionMETA.update({'id': item['id']}, dict(item), upsert=True)

		return item
