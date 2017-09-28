# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from scrapy.item import Item, Field
from scrapy.loader.processors import Compose, MapCompose
from appleMeta.utils import filter_empty

__author__ = 'Shanshan'

class App(Item):
	# define the fields for your item here like:
	id = Field()
	label = Field()
	app_name = Field()
	countries = Field()
	enabled = Field(input_processor=Compose(int))
	iphone = Field(input_processor=Compose(int))
	ipad = Field(input_processor=Compose(int))
	osx = Field(input_processor=Compose(int))
	description = Field(input_processor=Compose(MapCompose(unicode.strip), filter_empty))
	image_url = Field()
	app_store_url = Field()
	timestamp = Field()
	bundleId = Field()
	seller_name = Field()
	release_date = Field()
	price = Field(input_processor=Compose(float))
	genres = Field(input_processor=MapCompose(unicode.strip))
	rating_count_for_cur_version = Field(input_processor=Compose(int))
	content_rating_age_group = Field(input_processor=Compose(unicode.strip))
	avg_rating_for_cur_version = Field(input_processor=Compose(float))
	languages = Field(input_processor=MapCompose(unicode.strip))
	cur_ver_release_date = Field()
	app_type = Field()
	version = Field()
	currency = Field()
	# release_notes = Field(input_processor=Compose(MapCompose(unicode.strip), filter_empty))
	release_notes = Field()
	avg_rating = Field(input_processor=Compose(float))
	rating_count = Field(input_processor=Compose(int))
	min_os_version = Field()

	@property
	def key(self):
		return self._values['id']

	@property
	def export_filename(self):
		return 'app'