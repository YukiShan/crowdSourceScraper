import datetime
import re
# from scrapy import log
import scrapy
import logging
from scrapy.http import Request
from scrapy.selector import Selector
from urlparse import urljoin
from scraper.items import STJob
from scrapy.spider import BaseSpider
from scraper.utils import number_re, only_elem, SingleValItemLoader


__author__ = 'Shanshan'
xtract_id = re.compile(r'(?<=id=)\w+')


class STSpider(BaseSpider):
    name = 'shorttask'
    start_urls = ['http://www.shorttask.com/tasks.php']

    def parse(self, response):
        c_page = response.meta.get('page', 1)
        hxs = Selector(response)
        n_page = int(only_elem(hxs.xpath('//body//div[following-sibling::div[@class="main-content"]]/div[@class="task-top"]//a[contains(text(), "Last")]/@href').re(r'(?<=page=)\d+')))

        self.logger.info("Scraping jobs p%d" % c_page)

        for req in self.parse_job_list(response):
            yield req
        if c_page < n_page:
            yield Request('http://www.shorttask.com/tasks.php?page=%d' % (c_page + 1), meta={'page': c_page + 1})

    def parse_job_list(self, response):
        """
        Parses ShortTask Job List and crawls each job page
        """

        hxs = Selector(response)
        joblist = hxs.xpath('//body//div[@class="main-content"]/div[@class="template hits-tamplate"]')
        for job in joblist:
            job_expire = only_elem(job.xpath('(.//b[contains(text(), "Expires")]/following-sibling::text())[1]').re(r':\s+(.+)')).strip()
            job_href = only_elem(job.xpath('p[@class="view-task"]/a/@href').extract())
            job_id = xtract_id.search(job_href).group(0)
            job_url = urljoin(response.url, job_href)
            yield Request(job_url, callback=self.parse_single_job, meta={'job_expire': job_expire, 'job_id': job_id})

    def parse_single_job(self, response):
        """
        Parses a single Job and produces STJob item
        """

        self.logger.debug('Parsing job %s' % response.url)
        settings = self.crawler.settings

        hxs = Selector(response)
        # Abort not running jobs
        if hxs.xpath('//body//h3/text()').re('Sorry! This task is currently not active'):
            self.logger.info('Aborting inactive job %s' % response.url)
            return

        # Fill in the data of the job
        job = SingleValItemLoader(item=STJob(), response=response)
        job.add_value('timestamp', datetime.datetime.now().strftime(settings['TS_FMT']))
        job.add_value('expire', response.meta['job_expire'])
        job.add_value('id', response.meta['job_id'])
        job.add_value('url', response.url)

        parent_node = hxs.xpath('//body//div[@class="register-content"]')
        assert len(parent_node) == 1
        job.add_value('name', parent_node.xpath('(.//div[@class="task-top"]//b[contains(text(), "Title")]/following-sibling::text())[1]').extract())
        job.add_value('work_remain', parent_node.xpath('(.//div[@class="task-top"]//b[contains(text(), "Tasks Available")]/following-sibling::text())[1]').re(number_re))
        job.add_value('employer', parent_node.xpath('(.//div[@class="task-top"]//b[contains(text(), "Requester")]/following-sibling::text())[1]').extract())
        job.add_value('payment', parent_node.xpath('(.//div[@class="task-top"]//b[contains(text(), "Reward")]/following-sibling::text())[1]').re(number_re))
        job.add_value('duration', parent_node.xpath('(.//div[@class="task-top"]//b[contains(text(), "Duration")]/following-sibling::text())[1]').re(number_re))
        job.add_value('expected', parent_node.xpath('.//div[@class="box"][1]/following-sibling::div[@class="box" and following-sibling::div[@class="divider"]]//text()').extract())
        yield job.load_item()
