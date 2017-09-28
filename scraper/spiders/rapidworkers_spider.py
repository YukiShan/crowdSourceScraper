import datetime
import csv
# from scrapy import log
import scrapy
import logging
from scrapy.http import FormRequest, Request
from scrapy.selector import Selector
from urlparse import urljoin
from scraper.items import RWJob
from scrapy.spiders import Spider
from scraper.utils import number_re, only_elem, SingleValItemLoader
import re
import json
# from scrapy.shell import inspect_response
# inspect_response(response)

__author__ = 'Shanshan'

amazon_re = re.compile(r'[Aa][Mm][Aa]?[Zz][Oo]?[Nn]')
review_re = re.compile(r'[Rr][Ee][Vv][Ii][Ee][Ww][Ss]?|[Cc][Oo][Mm][Mm][Ee][Nn][Tt][Ss]?|[Qq][Uu][Ee][Ss][Tt][Ii][Oo][Nn][Ss]?')
amazonUrls_re = re.compile(r'(?:((https?://)?[\w\d?./=_-]+))')
# product_id_re = re.compile(r'(?:(?:/dp/)(\w+))')
product_id_re = re.compile(r'(?:(?:/gp/product/)|(?:/gp/product/glance/)|(?:/dp/))(\w+)')
review_id_re = re.compile(r'(?:(?:/review/)(\w+))')
url_re = re.compile(r'(?:(?:goo.gl/)([\w/]+))')


class RWSpider(Spider):
    name = 'rapidworkers'
    start_urls = ['http://rapidworkers.com/']

    def parse(self, response):
        if 'login_attempted' in response.meta:
            # check login succeed before going on
            if "The login credentials you supplied could not be recognized" in response.body:
                self.logger.error("Login failed")
                return
            else:
                return Request('http://rapidworkers.com/AvailableJobs/sort:modified/direction:desc', callback=self.parse_job_list)
        else:
            self.logger.info("Logging in")
            settings = self.crawler.settings
            return FormRequest.from_response(response, formname='loginfrm',
                                             formdata={'data[Member][email]': settings['SPIDER_LOGIN_EMAIL'],
                                                       'data[Member][password]': settings['SPIDER_LOGIN_PW']},
                                             meta={'login_attempted': True})

    def parse_job_list(self, response):
        """
        Parses Rapidworkers Job List and crawls each job page
        """

        self.logger.info("Scraping jobs")

        # hxs = Selector(response)
        record_re = re.compile(r'var records = (.*);')
        context = record_re.findall(response.body)
        # print context[0]
        jobs = json.loads(context[0])  
        for job in jobs:                      
            job_url = urljoin('http://rapidworkers.com/JobDetails/', job["Campaign"]["UUID"])
            # job_url = urljoin('http://rapidworkers.com/JobDetails/', "57305cb5-47b0-433c-b25f-4d483257911a")            
            yield Request(job_url, callback=self.parse_single_job)

    def parse_single_job(self, response):
        """
        Parses a single Job and produces RWJob item
        """

        self.logger.debug('Parsing job %s' % response.url)
        settings = self.crawler.settings
        hxs = Selector(response)
        # Abort not running jobs
        if hxs.xpath('//body//td/text()').re('This job is currently not running'):
            self.logger.info('Aborting not-running job %s' % response.url)
            return
        
        job = SingleValItemLoader(item=RWJob(), response=response)       
        # Fill in the data of the job
        parent_node = hxs.xpath('//body//div[@id="jobdetails"]')
        assert len(parent_node) == 1
        name = parent_node.xpath('(./div)[1]/ul/li/text()').re(r'Campaign Name\s*:\s+(.+)')
        # job.add_value('name', name)       

        hasAmazonInTitle = False
        hasRvwInTittle = False   
        hasAmazonInExpected = False
        hasRvmInExpected = False   
        hasAmazon = False
        hasRvm = False  
        if amazon_re.findall(name[0]):
            hasAmazonInTitle = True             
        if review_re.findall(name[0]):
            hasRvwInTittle = True 
        if (not hasAmazonInTitle) and (not hasRvwInTittle):    
            # self.logger.info('Not target job %s' % job._values['name'])
            self.logger.info('Not target job!')
            return     
        expected = parent_node.xpath('.//h3[contains(text(), "What is expected from workers")]/following-sibling::p//text()').extract()
        if amazon_re.findall(expected[0]):                
            hasAmazonInExpected = True
        if review_re.findall(expected[0]):                
            hasRvmInExpected = True
        hasAmazon = hasAmazonInTitle or hasAmazonInExpected
        hasRvw = hasRvwInTittle or hasRvmInExpected
        # print("<<<<<<>>>>>>>>>>>>")
        # print("hasAmazon = ", hasAmazon)
        # print("<<<<<<>>>>>>>>>>>>")
        # print("hasRvw = ", hasRvw)
        if (not hasAmazon) or (not hasRvw):
            self.logger.info('Not target job!')
            # print("<<<<<<>>>>>>>>>>>>")
            return 
        
        expectedContents = parent_node.xpath('.//h3[contains(text(), "What is expected from workers")]/following-sibling::p//text()').extract()
        urlsList = []
        for item in expectedContents:
            if amazonUrls_re.findall(item):
                resultUrls = amazonUrls_re.findall(item)
                for url in resultUrls:
                    if url[0].find("/") != -1:   

                        if url[0].find("document") != -1: 
                            # print(">>>>>>>>>>>>>1111111111<<<<<<<<<<<<<<<<<<")
                            # print(url[0])
                            # print(name)
                            strContents = ''.join(expectedContents)                        
                            with open(settings['SPIDER_SRC_FILENAME'], 'r') as read_file:
                                reader = csv.DictReader(read_file)
                                for src in reader:                                     
                                    if strContents.find(src['NAME']) != -1:
                                        # forming the url for each seed ID
                                        job.add_value('jobType', src['TYPE'])
                                        job.add_value('amazonId', src['ID'])  
                                        job.add_value('timestamp', datetime.datetime.now().strftime(settings['TS_FMT']))
                                        job.add_value('name', name)
                                        job.add_value('url', response.url)        
                                        job.add_value('id', parent_node.xpath('(./div)[1]/ul/li/text()').re(r'Campaign ID\s*:\s+(\S+)'))
                                        t = parent_node.xpath('(./div[1]/ul)[1]/li//text()').re(number_re)
                                        job.add_value('work_done', t[0])    
                                        job.add_value('work_total', t[1])
                                        job.add_value('payment', t[2])   
                                        job.add_value('duration', t[3])      
                                        job.add_value('countries', parent_node.xpath('(./div)[2]/ul/li/text()').re('\w+'))  
                                        yield job.load_item()   
                            continue
                                    
                        if url[0].find("amazon") != -1:
                            # print(">>>>>>>>>>>>>2222222222222<<<<<<<<<<<<<<<<<<")
                            # print(url[0])
                            # print(name)
                            if product_id_re.findall(url[0]):
                                prodIds = product_id_re.findall(url[0])
                                job.add_value('jobType', 'p')
                                job.add_value('amazonId', prodIds[0])     
                                
                            if review_id_re.findall(url[0]):                    
                                rvwIds = review_id_re.findall(url[0])                            
                                job.add_value('jobType', 'm')
                                job.add_value('amazonId', rvwIds[0]) 
                                                                                        
                            job.add_value('timestamp', datetime.datetime.now().strftime(settings['TS_FMT']))
                            job.add_value('name', name)
                            job.add_value('url', response.url)        
                            job.add_value('id', parent_node.xpath('(./div)[1]/ul/li/text()').re(r'Campaign ID\s*:\s+(\S+)'))
                            t = parent_node.xpath('(./div[1]/ul)[1]/li//text()').re(number_re)
                            job.add_value('work_done', t[0])    
                            job.add_value('work_total', t[1])
                            job.add_value('payment', t[2])   
                            job.add_value('duration', t[3])      
                            job.add_value('countries', parent_node.xpath('(./div)[2]/ul/li/text()').re('\w+'))  
                            yield job.load_item()    
                            continue

                        if (url[0].find("goo") != -1) or (url[0].find("amzn") != -1):  
                            global specialName, specialJobUrl, specialRspn
                            # specialName = name
                            # specialJobUrl = response.url
                            specialRspn = response
                            if (url[0].find('http') == -1):
                                if url_re.findall(url[0]):                                    
                                    # print(">>>>>>>>>>>>>2222222222222<<<<<<<<<<<<<<<<<<")
                                    # print(url_re.findall(url[0]))
                                    amz_url = urljoin('https://www.goo.gl/', url_re.findall(url[0])[0])                               
                                    yield Request(amz_url, callback=self.parse_amazon_url)
                            else:
                                yield Request(url[0], callback=self.parse_amazon_url)                           
                    
                        # urlsList.append(url[0]) 

        # job.add_value('amazonUrls', urlsList)     
        # job.add_value('amazonUrls', expectedContents)
        # print(">>>>>>>>>>>>>>test 8888888888 <<<<<<<<<<")
        # print(job._values['amazonUrls'])
        # job.add_value('proof', parent_node.xpath('.//h3[contains(text(), "Required proof that task was finished")]/following-sibling::p//text()').extract())
        # yield job.load_item()

    def parse_amazon_url(self, response):
        self.logger.info("Scraping amazon urls")
        settings = self.crawler.settings
        job = SingleValItemLoader(item=RWJob(), response=response) 
        # print(response.url)
        if product_id_re.findall(response.url):
            prodIds = product_id_re.findall(response.url)
            job.add_value('jobType', 'p')
            job.add_value('amazonId', prodIds[0])    
        
        if (response.url).find("google") != -1:
            # print(">>>>>>>>>>>>>2222222222222<<<<<<<<<<<<<<<<<<")
            # print(response.url)
            hxs = Selector(response)
            product_ids = hxs.xpath('//body//div[@role="listitem"]//div[contains(text(), "Review")]/a/text()').re(product_id_re)
            for prodct_id in product_ids:
                job.add_value('jobType', 'p')
                job.add_value('amazonId', prodct_id)

        if job._values['amazonId']:  
            hxsFormer = Selector(specialRspn)  
            parent_node = hxsFormer.xpath('//body//div[@id="jobdetails"]')
            assert len(parent_node) == 1
            name = parent_node.xpath('(./div)[1]/ul/li/text()').re(r'Campaign Name\s*:\s+(.+)')                                                        
            job.add_value('timestamp', datetime.datetime.now().strftime(settings['TS_FMT']))
            job.add_value('name', name)
            job.add_value('url', specialRspn.url)        
            job.add_value('id', parent_node.xpath('(./div)[1]/ul/li/text()').re(r'Campaign ID\s*:\s+(\S+)'))
            t = parent_node.xpath('(./div[1]/ul)[1]/li//text()').re(number_re)
            job.add_value('work_done', t[0])    
            job.add_value('work_total', t[1])
            job.add_value('payment', t[2])   
            job.add_value('duration', t[3])      
            job.add_value('countries', parent_node.xpath('(./div)[2]/ul/li/text()').re('\w+'))  
            yield job.load_item()                     


