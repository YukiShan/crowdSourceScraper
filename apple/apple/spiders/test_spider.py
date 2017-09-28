
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.http import Request

class AppleSpider(Spider):
    name = "apple"
    allowed_domains = ["apple.com"]
    start_urls = ["http://www.apple.com/itunes/charts/free-apps/"]


    def parse(self, response):
        hxs = Selector(response)        
        return Request('https://itunes.apple.com/us/reviews?userProfileId=215898480', callback=self.parse_job_list)


    def parse_job_list(self, response):
    	# print ">>>>>>>>>>>reviewer info<<<<<<<<<<<<"
    	# print response.url
    	print response.body