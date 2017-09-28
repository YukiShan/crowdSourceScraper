# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.conf import settings 
import pymongo

import scrapy
import logging
from twisted.enterprise import adbapi
from datetime import datetime
from hashlib import md5
import MySQLdb
import MySQLdb.cursors

class AppleMongoDBPipeline(object):
	def __init__(self):
		connectionAPP = pymongo.MongoClient(
			settings['MONGODB_SERVER'],
			settings['MONGODB_PORT']
			)
		connectionREV = pymongo.MongoClient(
			settings['MONGODB_SERVER'],
			settings['MONGODB_PORT']
			)
		connectionDEV = pymongo.MongoClient(
			settings['MONGODB_SERVER'],
			settings['MONGODB_PORT']
			)
		connectionRWR = pymongo.MongoClient(
			settings['MONGODB_SERVER'],
			settings['MONGODB_PORT']
			)
		
		db_app = connectionAPP[settings['MONGODB_ITUNES_APP_DB']]
		db_rev = connectionREV[settings['MONGODB_ITUNES_APP_DB']]
		db_dev = connectionDEV[settings['MONGODB_ITUNES_APP_DB']]
		db_rwr = connectionRWR[settings['MONGODB_ITUNES_APP_DB']]
		
		self.connectionAPP = db_app[settings['MONGODB_APP_COLLECTION']]
		self.connectionREV = db_rev[settings['MONGODB_REVIEW_COLLECTION']]
		self.connectionDEV = db_dev[settings['MONGODB_DEV_COLLECTION']]
		self.connectionRWR = db_rwr[settings['MONGODB_RWR_COLLECTION']]

		# random app database connection
		connectionRandAPP = pymongo.MongoClient(
			settings['MONGODB_SERVER'],
			settings['MONGODB_PORT']
			)
		connectionRandREV = pymongo.MongoClient(
			settings['MONGODB_SERVER'],
			settings['MONGODB_PORT']
			)
		connectionRandDEV = pymongo.MongoClient(
			settings['MONGODB_SERVER'],
			settings['MONGODB_PORT']
			)
		connectionRandRWR = pymongo.MongoClient(
			settings['MONGODB_SERVER'],
			settings['MONGODB_PORT']
			)
		
		db_rand_app = connectionRandAPP[settings['MONGODB_ITUNES_RAND_APP_DB']]
		db_rand_rev = connectionRandREV[settings['MONGODB_ITUNES_RAND_APP_DB']]
		db_rand_dev = connectionRandDEV[settings['MONGODB_ITUNES_RAND_APP_DB']]
		db_rand_rwr = connectionRandRWR[settings['MONGODB_ITUNES_RAND_APP_DB']]
		
		self.connectionRandAPP = db_rand_app[settings['MONGODB_RAND_APP_COLLECTION']]
		self.connectionRandREV = db_rand_rev[settings['MONGODB_RAND_REVIEW_COLLECTION']]
		self.connectionRandDEV = db_rand_dev[settings['MONGODB_RAND_DEV_COLLECTION']]
		self.connectionRandRWR = db_rand_rwr[settings['MONGODB_RAND_RWR_COLLECTION']]

	def process_item(self, item, spider):	
		connection = pymongo.MongoClient('localhost',27017)
		db_app = connection[settings['MONGODB_ITUNES_APP_DB']]
		db_rand_app = connection[settings['MONGODB_ITUNES_RAND_APP_DB']]

		if item.export_filename == 'app':
			self.connectionAPP.update({'id': item['id']}, dict(item), upsert=True)

		if item.export_filename == 'apps_related':
			res = db_app['updated_apps'].find_one({'id':item['id']})			
			if res:
				self.connectionAPP.update({'id': res['id']}, {$set : {'nApps_related':item['nApps_related'], 'app_ids_related':item['app_ids_related']}})

		if item.export_filename == 'review':
			self.connectionREV.update({'id': item['id']}, dict(item), upsert=True)    

		if item.export_filename == 'developer':
			res = db_app['updated_developers'].find_one({'id':item['id']})			
			if res:
				res['app_ids'] = list(set(res['app_ids'] + item['app_ids']))
				res['nApps_developed'] = len(res['app_ids'])
				res['timestamp'] = item['timestamp']
				self.connectionDEV.update({'id': res['id']}, dict(res), upsert=True)
			else:
				self.connectionDEV.insert(dict(item))		

		if item.export_filename == 'reviewer':
			res = db_app['updated_reviewers'].find_one({'id':item['id']})			
			if res:
				res['timestamp'] = item['timestamp']
				res['nApps_rvwed'] += item['nApps_rvwed']
				res['app_ids_rvwed'] += item['app_ids_rvwed']
				res['app_cats_rvwed'] += item['app_cats_rvwed']
				res['review_ratings'] += item['review_ratings']
				res['review_dates'] += item['review_dates']
				res['app_versions_rvwed'] += item['app_versions_rvwed']
				res['app_devIds_rvwed'] += item['app_devIds_rvwed']
				res['app_releaseDates_rvwed'] += item['app_releaseDates_rvwed']
				res['app_review_titles'] += item['app_review_titles']
				res['app_review_txts'] += item['app_review_txts']				
				self.connectionRWR.update({'id': res['id']}, dict(res), upsert=True)
			else:
				self.connectionRWR.insert(dict(item))		

		# random app stored in database
		if item.export_filename == 'rand_app':
			self.connectionRandAPP.update({'id': item['id']}, dict(item), upsert=True)

		if item.export_filename == 'rand_review':
			self.connectionRandREV.update({'id': item['id']}, dict(item), upsert=True)    

		if item.export_filename == 'rand_developer':			
			res = db_rand_app['developers'].find_one({'id':item['id']})
			if res:
				res['app_ids'] = list(set(res['app_ids'] + item['app_ids']))
				res['nApps_developed'] = len(res['app_ids'])
				res['timestamp'] = item['timestamp']
				self.connectionRandDEV.update({'id': item['id']}, dict(item), upsert=True)
			else:
				self.connectionRandDEV.insert(dict(item))

		if item.export_filename == 'rand_reviewer':
			res = db_rand_app['reviewers'].find_one({'id':item['id']})			
			if res:
				res['timestamp'] = item['timestamp']
				res['nApps_rvwed'] += item['nApps_rvwed']
				res['app_ids_rvwed'] += item['app_ids_rvwed']
				res['app_cats_rvwed'] += item['app_cats_rvwed']
				res['review_ratings'] += item['review_ratings']
				res['review_dates'] += item['review_dates']
				res['app_versions_rvwed'] += item['app_versions_rvwed']
				res['app_devIds_rvwed'] += item['app_devIds_rvwed']
				res['app_releaseDates_rvwed'] += item['app_releaseDates_rvwed']
				res['app_review_titles'] += item['app_review_titles']
				res['app_review_txts'] += item['app_review_txts']				
				self.connectionRandRWR.update({'id': res['id']}, dict(res), upsert=True)
			else:
				self.connectionRandRWR.insert(dict(item))

		return item


class AppleMySQLDBPipeline(object):
	def __init__(self, dbpool):
		self.dbpool = dbpool
	
	@classmethod
	def from_settings(cls, settings):
		dbargs = dict(
			host=settings['MYSQL_HOST'],
			db=settings['MYSQL_DB'],
			user=settings['MYSQL_USER'],
			passwd=settings['MYSQL_PASSWD'],
			port=settings['MYSQL_PORT'],
			charset='utf8',
			cursorclass = MySQLdb.cursors.DictCursor,
			use_unicode= True,
		)
		dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
		return cls(dbpool)

	
	def process_item(self, item, spider):
		d = self.dbpool.runInteraction(self._do_upinsert, item, spider)
		d.addErrback(self._handle_error, item, spider)
		d.addBoth(lambda _: item)
		return d


	def _do_upinsert(self, conn, item, spider):
		# now = datetime.utcnow().replace(microsecond=0).isoformat(' ')
		conn.execute("""
				select * from apps where id = %s
		""", (item["id"], ))
		ret = conn.fetchone()
		# print ">>>>>>>>>> ret <<<<<<<<<"
		# print ret 
		str_desc = ''.join(item['description'])
		str_genres = ''.join(item['genres'])
		str_lang = ''.join(item['languages'])
		# str_release_notes = ''.join(item['release_notes'])

		if ret:
			# print "running here 72"
			
			conn.execute("""
				UPDATE apps SET app_name = %s, countries = %s, enabled = %s, iphone = %s, ipad = %s, osx = %s, image_url = %s, app_store_url = %s, label = %s, 
				description = %s, timestamp = %s, bundleId = %s, seller_name = %s, release_date = %s, price = %s, genres = %s, rating_count_for_cur_version = %s, 
				content_rating_age_group = %s, avg_rating_for_cur_version = %s, languages = %s, cur_ver_release_date = %s, app_type = %s, version = %s, currency = %s, 
				release_notes = %s, avg_rating = %s, rating_count = %s, min_os_version = %s WHERE id = %s 
			""", (item['app_name'], item['countries'], item['enabled'], item['iphone'], item['ipad'], item['osx'], item['image_url'], item['app_store_url'], item['label'], 
				str_desc, item['timestamp'], item['bundleId'], item['seller_name'], item['release_date'], item['price'], str_genres, item['rating_count_for_cur_version'], 
				item['content_rating_age_group'], item['avg_rating_for_cur_version'], str_lang, item['cur_ver_release_date'], item['app_type'], item['version'], item['currency'], 
				item['release_notes'], item['avg_rating'], item['rating_count'], item['min_os_version'], item['id']))            
			# print "running here 22222"
		  
		else:
			# print "running here 84"

			# print( """
			#     INSERT INTO apps (id, app_name, countries, enabled, iphone, ipad, osx, image_url, app_store_url, label, description, timestamp, bundleId, seller_name, release_date, 
			#     price, genres, rating_count_for_cur_version, content_rating_age_group, avg_rating_for_cur_version, languages, cur_ver_release_date, app_type, version, currency, 
			#     release_notes, avg_rating, rating_count, min_os_version) 
			#     VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			# """, (item['id'], item['app_name'], item['countries'], item['enabled'], item['iphone'], item['ipad'], item['osx'], item['image_url'], item['app_store_url'], item['label'], 
			#     item['description'], item['timestamp'], item['bundleId'], item['seller_name'], item['release_date'], item['price'], item['genres'], item['rating_count_for_cur_version'], 
			#     item['content_rating_age_group'], item['avg_rating_for_cur_version'], item['languages'], item['cur_ver_release_date'], item['app_type'], item['version'], item['currency'], 
			#     item['release_notes'], item['avg_rating'], item['rating_count'], item['min_os_version']))

			conn.execute("""
				INSERT INTO apps (id, app_name, countries, enabled, iphone, ipad, osx, image_url, app_store_url, label, description, timestamp, bundleId, seller_name, release_date, 
				price, genres, rating_count_for_cur_version, content_rating_age_group, avg_rating_for_cur_version, languages, cur_ver_release_date, app_type, version, currency, 
				release_notes, avg_rating, rating_count, min_os_version) 
				VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			""", (item['id'], item['app_name'], item['countries'], item['enabled'], item['iphone'], item['ipad'], item['osx'], item['image_url'], item['app_store_url'], item['label'], 
				str_desc, item['timestamp'], item['bundleId'], item['seller_name'], item['release_date'], item['price'], str_genres, item['rating_count_for_cur_version'], 
				item['content_rating_age_group'], item['avg_rating_for_cur_version'], str_lang, item['cur_ver_release_date'], item['app_type'], item['version'], item['currency'], 
				item['release_notes'], item['avg_rating'], item['rating_count'], item['min_os_version']))
							
			# print "running here 94"
	

	
	def _handle_error(self, failure, item, spider):
		print failure
		self.logger.error(failure)

