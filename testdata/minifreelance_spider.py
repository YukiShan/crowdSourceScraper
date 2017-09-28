import datetime
# from scrapy import log
import scrapy
import logging
from scrapy.http import FormRequest, Request
from scrapy.selector import Selector
from urlparse import urljoin
from scraper.items import MFJob
from scrapy.spider import BaseSpider
from scraper.utils import number_re, some_txt_re, only_elem, only_elem_or_default, SingleValItemLoader


__author__ = 'Shanshan'


class MFSpider(BaseSpider):
    name = 'minifreelance'
    start_urls = ['http://minifreelance.com/login.php']

    def parse(self, response):
        if 'login_attempted' in response.meta:
            # check login succeed before going on
            if "Email and password don't match" in response.body:
                self.logger.error("Login failed")
                return
            else:
                return Request('http://minifreelance.com/jobs.php?Sort=NEWEST', callback=self.parse_job_list)
        else:
            self.logger.info("Logging in")
            settings = self.crawler.settings
            return FormRequest.from_response(response, formdata={'Email': settings['SPIDER_LOGIN_EMAIL'],
                                                                 'Password': settings['SPIDER_LOGIN_PW']},
                                             meta={'login_attempted': True})

    def parse_job_list(self, response):
        """
        Parses Minifreelance Job List and crawls each job page
        """

        self.logger.info("Scraping jobs")

        hxs = Selector(response)
        joblist = hxs.xpath('//body//div[@id="jobslist"]//tr[@name="RUNNING"]')
        for job in joblist:
            # success percentage is only available on the job list page, so it has to be passed to the task parser as an
            # additional piece of information
            job_success_pct = only_elem_or_default(job.xpath('td[12]/text()').re(number_re))
            job_url = only_elem(job.xpath('td[2]//a/@href').extract())
            job_url = urljoin(response.url, job_url)
            yield Request(job_url, callback=self.parse_single_job, meta={'job_success_pct': job_success_pct})

    def parse_single_job(self, response):
        """
        Parses a single Job and produces MFJob item
        """

        self.logger.debug('Parsing job %s' % response.url, level=log.DEBUG)
        settings = self.crawler.settings

        hxs = Selector(response)
        # Abort not running jobs
        if hxs.xpath('//body//td/text()').re('This job is currently not running'):
            self.logger.info('Aborting not-running job %s' % response.url)
            return

        # Fill in the data of the job
        job = SingleValItemLoader(item=MFJob(), response=response)
        job.add_value('timestamp', datetime.datetime.now().strftime(settings['TS_FMT']))
        job.add_value('success_pct', response.meta['job_success_pct'])
        job.add_value('url', response.url)

        parent_node = hxs.xpath('//body//table[@id="AutoNumber28"]')
        assert len(parent_node) == 1
        job.add_value('name', parent_node.xpath('(.//span)[1]/text()').re(some_txt_re))
        job.add_value('id', parent_node.xpath('(.//p)[1]/text()').re(r'Job ID:\s+(\w+)'))
        t = parent_node.xpath('(.//p)[1]//b/text()').re(number_re)
        job.add_value('work_done', t[0])
        job.add_value('work_total', t[1])
        job.add_value('payment', t[2])
        job.add_value('duration', t[3])
        countries = only_elem(parent_node.xpath('.//p[contains(b/text(), "You can accept this job if you are from these countries")]/following-sibling::table[1]//td/text()').re(some_txt_re))
        job.add_value('countries', [c.strip() for c in countries.split(',')])
        job.add_value('expected', parent_node.xpath('.//table[contains(.//b/text(), "What is expected from workers")]/following-sibling::p[following-sibling::table]/text()').extract())
        job.add_value('proof', parent_node.xpath('.//table[contains(.//td/b/text(), "proof")]/following-sibling::p[following-sibling::p[@style]]/text()').extract())
        yield job.load_item()
