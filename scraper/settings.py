# Scrapy settings for scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
import datetime
import os

BOT_NAME = 'Crowdsourcing Scraper'
USER_AGENT = 'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)'
ROBOTSTXT_OBEY = False
#COOKIES_ENABLED = False
LOG_LEVEL = 'INFO'
DOWNLOAD_DELAY = 0.25
RANDOMIZE_DOWNLOAD_DELAY = True


SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'

SPIDER_LOGIN_EMAIL = 'shanli.scuec@gmail.com'
SPIDER_LOGIN_PW = '523xyz'
SPIDER_LOGIN_PW2 = '523xyzLSS'
# SPIDER_LOGIN_PW3 = 'nfa08zii1'

# Pipeline
ITEM_PIPELINES = { 'scraper.pipelines.MongoDBPipeline': 800,
                   # 'scraper.pipelines.DuplicatesPipeline': 900,
                  # 'scraper.pipelines.InstantJsonExportPipeline': 1000,                  
                  }

# IO
TS_FMT = "%Y-%m-%d %H:%M:%S"
PROJECT_PATH = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
IO_PATH = os.path.join(PROJECT_PATH, 'io')
DATA_SET = 'same_cat_v2'
DATA_SET_DIR = os.path.join(PROJECT_PATH, 'io', DATA_SET)
SPIDER_SRC_FILENAME = os.path.join(DATA_SET_DIR, 'src.csv')

CRAWL_TS = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

#Database
MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_AMZN_TASK_DB = "rapidworkersAmazonTasks"
MONGODB_AMZN_TASK_COLLECTION = "amznSpamTasks"
MONGODB_APP_TASK_DB = "microworkersAppTasks"
MONGODB_APP_TASK_COLLECTION = "appPaidTasks"
