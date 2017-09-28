# -*- coding: utf-8 -*-

# Scrapy settings for apple project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
import os
from os import path

BOT_NAME = 'Apple Spider'
# USER_AGENT = 'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)'
USER_AGENT = 'iTunes/10.5.3 (Windows; Microsoft Windows 7 x64 Ultimate Edition Service Pack 1 (Build 7601)) AppleWebKit/534.52.7'
ROBOTSTXT_OBEY = False
COOKIES_ENABLED = False
LOG_LEVEL = 'INFO'
DOWNLOAD_DELAY = 0.25
RANDOMIZE_DOWNLOAD_DELAY = True

# Spider
SPIDER_MODULES = ['apple.spiders']
NEWSPIDER_MODULE = 'apple.spiders'
SPIDER_MIDDLEWARES = {
    'scrapy.spidermiddlewares.depth.DepthMiddleware': None,
    'apple.middlewares.iTunesDepthMiddleware': 901,
    'apple.middlewares.iTunesMaxPageMiddleware': 902,
}

# Pipeline
ITEM_PIPELINES = {  'apple.pipelines.AppleMongoDBPipeline': 800,
					# 'apple.pipelines.AppleMySQLDBPipeline': 800, 
                  }

# IO
TS_FMT = "%Y-%m-%d %H:%M:%S"
PROJECT_PATH = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
DATA_SET_DIR = path.join(PROJECT_PATH, 'io')
SPIDER_SEED_FILENAME = path.join(DATA_SET_DIR, 'seed.csv')

# Depth
DEPTH_LIMIT = 3
DEPTH_PRIORITY = 1
DEPTH_STATS_VERBOSE = True

SPIDER_APP_MAX_NPAGE = 10
SPIDER_DEV_MAX_NPAGE = 5
SPIDER_RWR_MAX_NPAGE = 30

#Mongo Database
MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_APP_TASK_DB = "microworkersAppTasks"
MONGODB_APP_TASK_COLLECTION = "appPaidTasks"

MONGODB_ITUNES_APP_DB = "appsFrmiTunes"
MONGODB_APP_COLLECTION = "updated_apps"
MONGODB_REVIEW_COLLECTION = "updated_reviews"
MONGODB_DEV_COLLECTION = "updated_developers"
MONGODB_RWR_COLLECTION = "updated_reviewers"

MONGODB_ITUNES_RAND_APP_DB = "randAppsFrmiTunes"
MONGODB_RAND_APP_COLLECTION = "apps"
MONGODB_RAND_REVIEW_COLLECTION = "reviews"
MONGODB_RAND_DEV_COLLECTION = "developers"
MONGODB_RAND_RWR_COLLECTION = "reviewers"


# MySQL Database
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_DB = 'reviews'
MYSQL_USER = 'root'
MYSQL_PASSWD = 'root'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'apple (+http://www.yourdomain.com)'



# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'apple.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'apple.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'apple.pipelines.SomePipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
