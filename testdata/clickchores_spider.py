import datetime
# from scrapy import log
import scrapy
import logging
from scrapy.http import FormRequest, Request
from scrapy.selector import Selector
from urlparse import urljoin
from scraper.items import CCJob, CCUser
import re
from scrapy.spider import BaseSpider
from scraper.utils import only_elem, SingleValItemLoader, country_re, number_re


__author__ = 'Shanshan'
xtract_id = re.compile(r'(?<=id=)\w+')


class MWSpider(BaseSpider):
    name = 'clickchores'
    start_urls = ['http://www.clickchores.com/loginif.php']

    def parse(self, response):
        if 'login_attempted' in response.meta:
            # check login succeed before going on
            if "Email and password don't match" in response.body:
                self.log("Login failed", level=log.ERROR)
                return
            else:
                return Request('http://www.clickchores.com/jobs.php?column=added&order=desc', callback=self.parse_job_list)
        else:
            self.log("Logging in", level=log.INFO)
            settings = self.crawler.settings
            return FormRequest.from_response(response, formdata={'username': settings['SPIDER_LOGIN_EMAIL'],
                                                                 'password': settings['SPIDER_LOGIN_PW']},
                                             meta={'login_attempted': True})

    def parse_job_list(self, response):
        """
        Parses ClickChores Job List and crawls each job page
        """

        self.logger.info("Scraping jobs and users")

        hxs = Selector(response)
        joblist = hxs.xpath('//body//div[@id="column_main"]//tr[@class="row_featured" or @class="row_even" or @class="row_odd"]')
        for job in joblist:
            job_url = only_elem(job.xpath('td[1]//a/@href').extract())
            job_url = urljoin(response.url, job_url)
            yield Request(job_url, callback=self.parse_single_job)

    def parse_single_job(self, response):
        """
        Parses a single Job and produces MWJob item
        """

        self.logger.debug('Parsing job %s' % response.url)
        settings = self.crawler.settings

        hxs = Selector(response)
        # Abort not running jobs
        if hxs.xpath('//body//td/text()').re('This job is currently not running'):
            self.logger.info('Aborting not-running job %s'%response.url)
            return

        # Fill in the data of the job
        job = SingleValItemLoader(item=CCJob(), response=response)
        job.add_value('timestamp', datetime.datetime.now().strftime(settings['TS_FMT']))
        job.add_value('url', response.url)

        parent_node = hxs.xpath('//body//div[@id="column_main"]')
        assert len(parent_node) == 1
        job.add_value('name', parent_node.xpath('h1[1]/text()').extract())
        t = parent_node.xpath('h1[1]/following-sibling::table//td[1]')
        job.add_value('countries', t.xpath('p[contains(.//text(), "any of these countries")]/following-sibling::span[./following-sibling::h3[contains(text(), "Job Description")]]/text()').re(country_re))
        job.add_value('expected', t.xpath('(h3[contains(text(), "Job Description")]/following-sibling::p)[1]/text()').extract())
        job.add_value('proof', t.xpath('(h3[contains(text(), "Required proof that job was finished")]/following-sibling::p)[1]/text()').extract())
        t = parent_node.xpath('h1[1]/following-sibling::table//td[2]//div[contains(h3/text(), "Job Details")]')
        job.add_value('id', t.xpath('text()').re(r'Job ID:\s+(\w+)'))
        job.add_value('featured', t.xpath('./span[@class="featured"]'))
        tt = t.xpath('.//b/text()').re(number_re)
        job.add_value('payment', tt[0])
        work_total = int(tt[1])
        work_remain = int(only_elem(t.xpath('text()[contains(., "Available Positions")]/following-sibling::span/text()').re(number_re)))
        job.add_value('work_total', work_total)
        job.add_value('work_done', work_total - work_remain)
        job.add_value('success_pct', t.xpath('text()').re(r'Success:\s+(' + number_re + ')'))
        job.add_value('duration', t.xpath('text()').re(r'\d+(?= minutes to complete)'))
        job.add_value('cat', t.xpath('.//a/text()').extract())
        href = only_elem(parent_node.xpath('h1[1]/following-sibling::table//td[2]//div[contains(h3/text(), "About the Employer")]//b/a/@href').extract())
        job.add_value('employer', xtract_id.search(href).group(0))
        yield job.load_item()
        user_url = urljoin(response.url, href)
        yield Request(user_url, callback=self.parse_single_user)

    def parse_single_user(self, response):
        """
        Parses a single page of user
        """

        self.logger.debug('Parsing user %s' % response.url)
        settings = self.crawler.settings

        user = SingleValItemLoader(item=CCUser(), response=response)
        user.add_value('timestamp', datetime.datetime.now().strftime(settings['TS_FMT']))
        user.add_value('url', response.url)

        hxs = Selector(response)
        # fill in the details of user
        user.add_value('name', hxs.xpath('//div[@id="column_main"]//h2/text()').extract())
        t = hxs.xpath('(//div[@id="column_main"]//h2/following-sibling::div)[1]')
        user.add_value('id', t.xpath('text()').re(r'ID:\s+(\w+)'))
        user.add_value('country', t.xpath('(text()[contains(., "Country")]/following-sibling::text())[1]').re(r'\w+(?:(?:\s+\w+)+)?'))
        user.add_value('member_since', t.xpath('text()').re(r'Member Since:\s+(.+)'))
        w_stat = hxs.xpath('//div[@id="column_main"]//div[@class="profile_stats" and contains(h3/text(), "Worker Statistics")]')
        if w_stat:
            user.add_value('tasks_done', w_stat.xpath('(label[contains(text(), "Jobs Complete")]/following-sibling::text())[1]').re(number_re))
            user.add_value('tasks_satisfied', w_stat.xpath('(label[contains(text(), "Satisfied")]/following-sibling::text())[1]').re(number_re))
            user.add_value('tasks_not_satisfied', w_stat.xpath('(label[contains(text(), "Not Satisfied")]/following-sibling::text())[1]').re(number_re))
            user.add_value('avg_per_task_earned', w_stat.xpath('(label[contains(text(), "Average Job Price")]/following-sibling::text())[1]').re(number_re))
            user.add_value('total_earned', w_stat.xpath('(label[contains(text(), "Total Earned")]/following-sibling::text())[1]').re(number_re))
        e_stat = hxs.xpath('//div[@id="column_main"]//div[@class="profile_stats" and contains(h3/text(), "Employer Statistics")]')
        if e_stat:
            user.add_value('tasks_paid', e_stat.xpath('(label[contains(text(), "Jobs Posted")]/following-sibling::text())[1]').re(number_re))
            user.add_value('avg_per_task_paid', e_stat.xpath('(label[contains(text(), "Average Job Price")]/following-sibling::text())[1]').re(number_re))
            user.add_value('total_paid', e_stat.xpath('(label[contains(text(), "Total Spend")]/following-sibling::text())[1]').re(number_re))
        yield user.load_item()
