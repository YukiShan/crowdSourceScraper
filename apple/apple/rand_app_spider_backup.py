
__author__ = 'Shanshan'

import datetime
# from scrapy import log
import scrapy
import logging
from scrapy.http import FormRequest, Request
from scrapy.selector import Selector
from scrapy.utils.misc import arg_to_iter
from urlparse import urljoin
from apple.items import RandApp, RandReview, RandDeveloper
import re
from scrapy.spiders import Spider
from apple.utils import SingleValItemLoader, only_elem, only_elem_or_default, APP_TYPE, DEV_TYPE
# from apple.rank import get_rank
import pymongo
import json
import feedparser
import calendar
import csv

app_id_re = r'(?:(?:/id))(\w+)'
app_rvwer_id_re = re.compile(r'(?:(?:/id))(\w+)')
app_rvw_id_re = re.compile(r'(?:(?:mostRecent/))(\w+)')
app_page_re = re.compile(r'(?:(?:/page=))(\w+)')

app_countries = {
		'China':'cn',
		'United States':'us'
}

app_sortby = {
		'Most Recent':'mostRecent',
		'Most Helpful':'mostHelpful',
		'Most Favorable':'mostFavorable',
		'Most Critical':'mostCritical'
}

def _app_details_url(app_id):
		s = 'https://itunes.apple.com/lookup?id=%s' % app_id
		return s

def _app_rev_url(app_id, page=1, country_code = app_countries['United States'], sortby= app_sortby['Most Recent']):
		s = 'https://itunes.apple.com/%s/rss/customerreviews/page=%d/id=%s/sortBy=%s/xml' % (country_code, page, app_id, sortby)
		return s

def _dev_profile_url(dev_id):
		s = 'https://itunes.apple.com/us/developer/id%s' % dev_id
		return s

class AppleSpider(Spider):
		name = 'randAppReviews'
		allowed_domains = ["itunes.apple.com"]

		def __init__(self, **kwargs):
				super(AppleSpider, self).__init__(**kwargs)        
				self.app_req_param = {
															APP_TYPE: (_app_details_url, self.parse_app_details_page),
															DEV_TYPE: (_dev_profile_url, self.parse_dev_profile_page)
															}

				self.rev_req_param = {
															APP_TYPE: (_app_rev_url, self.parse_app_rev_page)															
															}

		def _item_info_request(self, id_, type_, referrer):
				app_url_gen, cb = self.app_req_param[type_]
				req_meta = {'id': id_, 'type': type_, 'referrer': referrer}        
				return Request(app_url_gen(id_), callback=cb, meta=req_meta)

		def _rev_page_request(self, id_, type_, p=1):
				rev_url_gen, cb = self.rev_req_param[type_]
				req_meta = {'id': id_, 'type': type_, 'page': p}
				return Request(rev_url_gen(id_, p), callback=cb, meta=req_meta)

		def _successor_page_request(self, response):
				type_, id_ = response.meta['type'], response.meta['id']
				next_p = response.meta['page'] + 1
				return self._rev_page_request(id_, type_, next_p)

		def start_requests(self):
				"""
				read seed data from seed.csv

				"""
				settings = self.crawler.settings
				reqs = []

				with open(settings['SPIDER_SEED_FILENAME'], 'r') as read_file:
					reader = csv.DictReader(read_file)
					for seed in reader:         
						app_platform = seed['Platform']
						app_id = seed['ID']             
						try:
							if app_platform == 'App store':	                    
								req = self._item_info_request(app_id, APP_TYPE, referrer=None)
						except KeyError:
							raise ValueError("App with ID %s in %s platform is not available currently." % (app_id, app_platform))
						reqs += arg_to_iter(req)
				return reqs

		def parse_app_details_page(self, response):
				"""
				Parses app basic info in app store
				"""

				settings = self.crawler.settings
				self.logger.info('Parsing app info: %s' % response.meta['id'])
				context = json.loads(response.body)['results']
				if not context:
					self.logger.info("App with ID %s in App Store is not available currently." % (response.meta['id']))
					return	
				app_context = context[0]
				
				rand_app = SingleValItemLoader(item=RandApp(), response=response) 
				app_id = response.meta['id'] 				
				rand_app.add_value('id', app_id)
				app_referrer = response.meta['referrer']   
				rand_app.add_value('referrer', app_referrer)
				# if app_referrer == "Crowdsourced":
				# 	rand_app.add_value('label', 'paid-app')
				# else:
				# 	rand_app.add_value('label', 'unknown-app')
				rand_app.add_value('app_name', app_context['trackName'])        
				rand_app.add_value('countries', 'us')        
				rand_app.add_value('enabled', app_context['isVppDeviceBasedLicensingEnabled'])        
				if app_context['kind'] == 'mac-software':
					rand_app.add_value('iphone', 0)
					rand_app.add_value('ipad', 0)
					rand_app.add_value('osx', 1)
				else:
					rand_app.add_value('iphone', 1)
					rand_app.add_value('ipad', 1)
					rand_app.add_value('osx', 0)       	
				rand_app.add_value('description', app_context['description'])       	
				rand_app.add_value('image_url', app_context['artworkUrl60'])       	
				rand_app.add_value('app_store_url', app_context['trackViewUrl'])       	
				rand_app.add_value('timestamp', datetime.datetime.now().strftime(settings['TS_FMT']))
				rand_app.add_value('bundleId', app_context['bundleId'])  
				rand_app.add_value('developer_name', app_context['artistId'])       	
				rand_app.add_value('developer_name', app_context['sellerName'])       	
				rand_app.add_value('release_date', app_context['releaseDate'])       	
				rand_app.add_value('price', app_context['price'])       	
				rand_app.add_value('genres', app_context['genres'])  
				rand_app.add_value('main_cat', app_context['primaryGenreName'])     	  	
				rand_app.add_value('content_rating_age_group', app_context['trackContentRating'])       	   	
				rand_app.add_value('languages', app_context['languageCodesISO2A'])       	
				rand_app.add_value('cur_ver_release_date', app_context['currentVersionReleaseDate'])       	
				rand_app.add_value('app_type', app_context['wrapperType'])       	
				rand_app.add_value('version', app_context['version'])       	     	
				rand_app.add_value('currency', app_context['currency'])
				rand_app.add_value('min_os_version', app_context['minimumOsVersion'])  
				# rank_map, rank_list_name = get_rank(app_id, rand_app._values['main_cat'])
				# if not rank_map:
				# 	self.logger.info('App has no available rank!')
				# 	rand_app.add_value('rank', 0)
				# 	rand_app.add_value('rank_list_name', None)					
				# else:
				# 	rand_app.add_value('rank', rank_map['rank'])
				# 	rand_app.add_value('rank_list_name', rank_list_name) 	    
				try:
					rand_app.add_value('avg_rating_for_cur_version', app_context['averageUserRatingForCurrentVersion'])
				except KeyError:
					self.logger.info('Index does not exist!')
					rand_app.add_value('avg_rating_for_cur_version', 0)       	
				try: 
					rand_app.add_value('rating_count_for_cur_version', app_context['userRatingCountForCurrentVersion'])
				except KeyError:
					self.logger.info('Index does not exist!')
					rand_app.add_value('rating_count_for_cur_version', 0)       	
				try:
					rand_app.add_value('avg_rating', app_context['averageUserRating'])
				except KeyError:
					self.logger.info('Index does not exist!')
					rand_app.add_value('avg_rating', 0)       	
				try:
					rand_app.add_value('rating_count', app_context['userRatingCount'])
				except KeyError:
					self.logger.info('Index does not exist!')
					rand_app.add_value('rating_count', 0)
				try:
					rand_app.add_value('release_notes', app_context['releaseNotes'])
				except KeyError:
					self.logger.info('Index does not exist!')
					rand_app.add_value('release_notes', 0)       	  	 
				
				yield rand_app.load_item()

				#yield the app reviews page
				yield self._rev_page_request(app_id, APP_TYPE)

				#yield the app related page.
				yield Request(rand_app._values['app_store_url'], callback=self.parse_app_related_page, 
					meta= {'id': app_id, 'type': APP_TYPE, 'referrer': app_id})


		def parse_app_rev_page(self, response):
				"""
				Parses at most 500 app reviews in app store
				"""
				# Start parsing this page
				self.logger.info('Parsing app reviews: %s  p%d' % (response.meta['id'], response.meta['page']))
				settings = self.crawler.settings  
				feed = feedparser.parse(response.url)        

				if not feed.entries:
						self.logger.info('Get nothing from %s'% response.url)
						return 
				
				for entry in feed.entries[1:]:
						rand_review = SingleValItemLoader(item=RandReview(), response=response)
						rand_review.add_value('id', app_rvw_id_re.findall(entry['id'])[0])
						rand_review.add_value('timestamp', datetime.datetime.now().strftime(settings['TS_FMT']))
						rand_review.add_value('title', entry['title'])						
						rand_review.add_value('app_id', response.meta['id'])
						rand_review.add_value('comment', entry['content'][0]['value'])
						rand_review.add_value('author_name', entry['author'])						
						rand_review.add_value('author_id', app_rvwer_id_re.findall(entry['authors'][0]['href'])[0])
						rand_review.add_value('starRating', entry['im_rating'])
						rand_review.add_value('version', entry['im_version'])
						rand_review.add_value('vote', entry['im_votecount'])
						rand_review.add_value('country', 'us')
						rand_review.add_value('updated', datetime.datetime.fromtimestamp
							(int(calendar.timegm(entry['updated_parsed']))).strftime(settings['TS_FMT']))
						# print(">>>>>>>test here 210 <<<<<<<<<<<")						
						# print(rand_review._values['updated'])						

						yield rand_review.load_item()
						
				# request subsequent pages to be downloaded
				# Find out the number of review pages
				noPages = int(app_page_re.findall(feed.feed['links'][3]['href'])[0])
				# print(">>>>>>>test here 210 <<<<<<<<<<<")						
				# print(noPages)
				if response.meta['page'] < noPages:
						yield self._successor_page_request(response)


		def parse_app_related_page(self, response):
				"""
				Parses apps from an app related page in app store
				"""

				self.logger.info('Parsing apps related to: %s' % response.meta['id'])
				settings = self.crawler.settings  
				hxs = Selector(response)

				apps_ids_bought = hxs.xpath('//body//div[contains(h2/text(), "Customers Also Bought")]/following-sibling::div[@num-items="5"]//a[@class="artwork-link"]/@href').re(app_id_re)				
				if apps_ids_bought: 
					for app_id in apps_ids_bought:
						yield self._item_info_request(str(app_id), APP_TYPE, referrer=response.meta['referrer'])	

				dev_id = hxs.xpath('//body//a[contains(text(), "View More by This Developer")]/@href').re(app_id_re)
				# print(">>>>>>>test here 22222 <<<<<<<<<<<")
				# print(dev_id)
				if dev_id:
					yield self._item_info_request(dev_id, DEV_TYPE, referrer=response.meta['referrer'])
				

		def parse_dev_profile_page(self, response):
				"""
					Parses apps from same developer in app store
				"""
				self.logger.info('Parsing apps of the same developer as %s:' % response.meta['id'])
				settings = self.crawler.settings  
				hxs = Selector(response)
				rand_developer = SingleValItemLoader(item=RandDeveloper(), response=response)
				
				name = hxs.xpath('//body//h1[@itemprop="name"]/text()').extract()
				rand_developer.add_value('id', response.meta['id'])
				rand_developer.add_value('name', name)
				rand_developer.add_value('timestamp', datetime.datetime.now().strftime(settings['TS_FMT']))
				rand_developer.add_value('referrer', response.meta['referrer'])

				app_type1 = hxs.xpath('//body//div[metrics-loc="Titledbox_iPhone Apps"]')
				app_type2 = hxs.xpath('//body//div[metrics-loc="Titledbox_iPad Apps"]')
				app_type3 = hxs.xpath('//body//div[metrics-loc="Titledbox_Mac Apps"]')
				app_type4 = hxs.xpath('//body//div[metrics-loc="Titledbox_App Bundles"]')

				apps = hxs.xpath('//body//a[@class="artwork-link"]/@href')			
				if len(apps) == 1 and only_elem(apps.re(app_id_re)) == response.meta['referrer']:
					self.logger.info(r'Aborting unavailable developer page: %s' % response.url)
					rand_developer.add_value('nApps_developed', 1)
					rand_developer.add_value('app_ids', response.meta['referrer'].decode('utf-8', 'ignore'))
					if app_type1:
						rand_developer.add_value('app_type_developed', u'iPhone Apps')
					elif app_type2:
						rand_developer.add_value('app_type_developed', u'iPad Apps')
					elif app_type3:
						rand_developer.add_value('app_type_developed', u'Mac Apps')
					else:
						rand_developer.add_value('app_type_developed', u'App Bundles')

					yield rand_developer.load_item()
					return

				app_ids = apps.re(app_id_re)
				app_ids = list(set(app_ids))
				rand_developer.add_value('nApps_developed', len(app_ids))				
				rand_developer.add_value('app_ids', app_ids)
				app_types = []
				if app_type1:
					app_types.append(u'iPhone Apps')
				if app_type2:
					app_types.append(u'iPad Apps')
				if app_type3:
					app_types.append(u'Mac Apps')
				if app_type4:
					app_types.append(u'App Bundles')
				rand_developer.add_value('app_type_developed', app_types)
				yield rand_developer.load_item()

				for app_id in app_ids:
					yield self._item_info_request(str(app_id), APP_TYPE, referrer=response.meta['id'])	
				
