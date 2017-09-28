import datetime
# from scrapy import log
import scrapy
import logging
from scrapy.http import FormRequest, Request
from scrapy.selector import Selector
from scraper.items import JBJob
from scrapy.spiders import Spider
from urlparse import urljoin
from scraper.utils import number_re, some_txt_re, SingleValItemLoader, only_elem_or_default, only_elem
import re

# from scrapy.shell import inspect_response
# inspect_response(response)

__author__ = 'Shanshan'

amazon_re = re.compile(r'[Aa]mazon')
review_re = re.compile(r'[Rr]eviews?|[Cc]omments?')

class JBSpider(Spider):
    name = 'scraper'
    start_urls = ['http://www.jobboy.com']

    def parse(self, response):
        if 'login_attempted' in response.meta:
            # check login succeed before going on
            hxs = Selector(response)
            if hxs.xpath('//div[@id="error"]//cufontext[contains(text(), "incorrect.")]'):
                self.logger.error("Login failed")
                return
            else:
                self.logger.debug("Login succeeded")
                return Request('http://www.jobboy.com/index.php?inc=user-0&action=jobsavailable', meta={'page': 0},
                               callback=self.parse_job_list)
        else:
            self.logger.info("Logging in")
            settings = self.crawler.settings
            return FormRequest.from_response(response,
                                             formdata={'email': settings['SPIDER_LOGIN_EMAIL'],
                                                       'password': settings['SPIDER_LOGIN_PW']},
                                             meta={'login_attempted': True})

    def parse_job_list(self, response):
        """
        Parses Jobboy Job List and crawls each job page
        """

        self.logger.info("Scraping jobs")

        hxs = Selector(response)
        joblist = hxs.xpath('//body//div[@id="si-content"]//tbody//tr')
        for job in joblist:
            job_success_pct = only_elem_or_default(job.xpath('./td[4]/text()').re(number_re))
            job_url = only_elem(job.xpath('.//a/@href').extract())
            # total_url = urljoin('http://www.jobboy.com/', job_url)
            # print(">>>>>>>test here 150 <<<<<<<<<<<")
            # print(total_url)
            yield Request(urljoin('http://www.jobboy.com/', job_url), callback=self.parse_single_job, meta={'job_success_pct': job_success_pct})
        n_pages = int(only_elem(hxs.xpath('//body//div[@id="si-content"]//tfoot//tr//text()').re(r'\d+ of\s+(\d+)'))) - 1
        current_p = response.meta['page']
        if current_p < n_pages:
            self.logger.debug("Parsing another page of jobs")
            yield Request('http://www.jobboy.com/index.php?inc=user-%d&action=jobsavailable' % (current_p + 1),
                          meta={'page': current_p + 1}, callback=self.parse_job_list)

    def parse_single_job(self, response):
        """
        Parses a single Job and produces JBJob item
        """

        self.logger.debug('Parsing job %s' % response.url)

        hxs = Selector(response)
        settings = self.crawler.settings
        # Abort not running jobs
        if hxs.xpath('//body//td/text()').re('This job is currently not running'):
            self.logger.info('Aborting not-running job %s' % response.url)
            return

        job = SingleValItemLoader(item=JBJob(), response=response)

        hasAmazon = False
        hasReview = False

        job.add_value('expected', hxs.xpath('//div[@id="si-content"]//strong[contains(text(), "Job Description")]/following-sibling::p[1]/text()').extract())
        for item in job._values['expected']: 
            if amazon_re.findall(item):
                hasAmazon = True
            if review_re.findall(item):
                hasReview = True
            if hasAmazon and hasReview:
                job.add_value('timestamp', datetime.datetime.now().strftime(settings['TS_FMT']))
                job.add_value('url', response.url)
                job.add_value('success_pct', response.meta['job_success_pct'])
                detail_pane_node = hxs.xpath('//div[@class="container"]/div[contains(@style, "margin:") and contains(@style, "padding:")]')
                t = detail_pane_node.xpath('.//h4/text()').re(number_re)
                job.add_value('payment', t[0])
                job.add_value('duration', t[1])
                job.add_value('work_done', t[2])
                job.add_value('work_total', t[3])
                job.add_value('id', hxs.xpath('//div[@class="signup"]/div[contains(@style, "margin:") and contains(@style, "padding:")]/form/@action').re(number_re))
                job.add_value('name', hxs.xpath('//div[@id="si-content"]//h2//text()').extract())
                yield job.load_item()
                break
        

        # Fill in the data of the job
        
        # cat_node = hxs.xpath('(//div[@id="si-content"]/div[@class="signup"]/strong)[1]')
        # job.add_value('cat', cat_node.xpath('./text()').re(some_txt_re))
        # job.add_value('sub_cat', cat_node.xpath('(./following-sibling::text())[1]').re(r'(?:-\s+)?(' + some_txt_re + ')'))
        # countries = only_elem(hxs.xpath('//div[@id="si-content"]//strong[contains(text(), "This job is available to")]/following-sibling::text()').re(some_txt_re))
        # job.add_value('countries', [c.strip() for c in countries.split('+')])
        
        # job.add_value('proof', hxs.xpath('//div[@id="si-content"]//strong[contains(text(), "How to prove you done it")]/following-sibling::text()').extract())
        
           
        # yield job.load_item()
