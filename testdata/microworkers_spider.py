import datetime
# from scrapy import log
import scrapy
import logging
from scrapy.http import FormRequest, Request
from scrapy.selector import Selector
from urlparse import urljoin
from scraper.items import MWJob, MWUser
import re
from scrapy.spider import BaseSpider
from scraper.utils import country_re, number_re, some_txt_re, SingleValItemLoader, only_elem


__author__ = 'Shanshan'
xtract_id = re.compile(r'(?<=Id=)\w+')


class MWSpider(BaseSpider):
    name = 'microworkers'
    start_urls = ['https://microworkers.com/login.php']

    def parse(self, response):
        if 'login_attempted' in response.meta:
            # check login succeed before going on
            if "Email and password don't match" in response.body:
                self.logger.debug("Login failed")
                return
            else:
                return Request('https://microworkers.com/jobs.php?Sort=NEWEST&Id_category=ALL', callback=self.parse_job_list)
        else:
            self.logger.info("Logging in")
            settings = self.crawler.settings
            return FormRequest.from_response(response, formdata={'Email': settings['SPIDER_LOGIN_EMAIL'],
                                                                 'Password': settings['SPIDER_LOGIN_PW2']},
                                             meta={'login_attempted': True})

    def parse_job_list(self, response):
        """
        Parses Microworkers Job List and crawls each job page
        """

        self.logger.info("Scraping jobs and users")

        hxs = Selector(response)
        joblist = hxs.xpath('//body//div[@id="jobslist"]//tr[@name="RUNNING"]')
        for job in joblist:
            # success percentage is only available on the job list page, so it has to be passed to the task parser as an
            # additional piece of information
            job_success_pct = only_elem(job.xpath('td[4]/text()').extract()).strip()
            job_url = only_elem(job.xpath('td[2]//a/@href').extract())
            job_url = urljoin(response.url, job_url)
            yield Request(job_url, callback=self.parse_single_job, meta={'job_success_pct': job_success_pct})

    def parse_single_job(self, response):
        """
        Parses a single Job and produces MWJob item
        """

        self.logger.debug('Parsing job %s' % response.url)
        settings = self.crawler.settings

        hxs = Selector(response)
        # Abort not running jobs
        if hxs.xpath('//body//td/text()').re('This job is currently not running'):
            self.logger.info('Aborting not-running job %s' % response.url)
            return

        # Fill in the data of the job
        job = SingleValItemLoader(item=MWJob(), response=response)
        job.add_value('timestamp', datetime.datetime.now().strftime(settings['TS_FMT']))
        job.add_value('success_pct', response.meta['job_success_pct'])
        job.add_value('url', response.url)

        parent_node = hxs.xpath('//body//table//table//table//td[@width="520"]')
        assert len(parent_node) == 1
        job.add_value('name', parent_node.xpath('span[1]/text()').extract())
        job.add_value('id', parent_node.xpath('table[2]//td[1]/p/text()').re(r'Job ID:\s+(\w+)'))
        t = parent_node.xpath('table[2]//td[1]/p//b/text()').re(number_re)
        job.add_value('work_done', t[0])
        job.add_value('work_total', t[1])
        job.add_value('payment', t[2])
        job.add_value('duration', t[3])
        href = only_elem(parent_node.xpath('table[2]//a/@href').extract())
        job.add_value('employer', xtract_id.search(href).group(0))
        job.add_value('countries', parent_node.xpath('table[3]//p/text()').re(country_re))
        job.add_value('cat', parent_node.xpath('p[1]//b/text()').re(some_txt_re))
        job.add_value('sub_cat', parent_node.xpath('p[1]/text()').re(some_txt_re))
        job.add_value('expected', parent_node.xpath('table[4]//td[1]/p[1]//text()').extract())
        job.add_value('proof', parent_node.xpath('table[4]//td[1]/p[3]//text()').extract())
        yield job.load_item()
        user_url = urljoin(response.url, href)
        yield Request(user_url, callback=self.parse_single_user)

    def parse_single_user(self, response):
        """
        Parses a single page of user
        """

        self.logger.debug('Parsing user %s' % response.url)
        settings = self.crawler.settings

        user = SingleValItemLoader(item=MWUser(), response=response)
        user.add_value('timestamp', datetime.datetime.now().strftime(settings['TS_FMT']))
        user.add_value('url', response.url)

        hxs = Selector(response)

        # fill in the details of user
        user.add_value('name', hxs.xpath('//table[@id="AutoNumber64"]//td[contains(text(), "Nickname")]/following-sibling::td/b/text()').extract())
        user.add_value('id', hxs.xpath('//table[@id="AutoNumber64"]//td[contains(text(), "ID")]/following-sibling::td/text()').extract())
        user.add_value('member_since', hxs.xpath('//table[@id="AutoNumber64"]//td[contains(text(), "Member since")]/following-sibling::td/text()').extract())
        user.add_value('country', hxs.xpath('//table[@id="AutoNumber64"]//td[contains(text(), "Country")]/following-sibling::td/text()').re(some_txt_re))
        user.add_value('city', hxs.xpath('//table[@id="AutoNumber64"]//td[contains(text(), "City")]/following-sibling::td/text()').re(some_txt_re))
        user.add_value('total_earned', hxs.xpath('//table[@id="AutoNumber91"]//td[contains(b/text(), "Total Earned")]/following-sibling::td/b/text()').re(number_re))
        user.add_value('tasks_done', hxs.xpath('//table[@id="AutoNumber91"]//td[contains(text(), "Tasks done")]/following-sibling::td/text()').re(number_re))
        user.add_value('basic_tasks', hxs.xpath('//table[@id="AutoNumber92"]//td[contains(b/text(), "Basic tasks")]/following-sibling::td/b/text()').re(number_re))
        user.add_value('basic_satisfied', hxs.xpath('//table[@id="AutoNumber92"]//td[contains(text(), "Satisfied") and not(contains(text(), "Not"))]/following-sibling::td/text()').re(number_re))
        user.add_value('basic_not_satisfied', hxs.xpath('//table[@id="AutoNumber92"]//td[contains(text(), "Not-Satisfied")]/following-sibling::td/text()').re(number_re))
        user.add_value('basic_avg_per_task', hxs.xpath('//table[@id="AutoNumber92"]//td[contains(text(), "Average per task")]/following-sibling::td/text()').re(number_re))
        user.add_value('hg_tasks', hxs.xpath('//table[@id="AutoNumber93"]//td[contains(b/text(), "Hire Group")]/following-sibling::td/b/text()').re(number_re))
        user.add_value('hg_satisfied', hxs.xpath('//table[@id="AutoNumber93"]//td[contains(text(), "Satisfied") and not(contains(text(), "Not"))]/following-sibling::td/text()').re(number_re))
        user.add_value('hg_not_satisfied', hxs.xpath('//table[@id="AutoNumber93"]//td[contains(text(), "Not-Satisfied")]/following-sibling::td/text()').re(number_re))
        user.add_value('hg_avg_per_task', hxs.xpath('//table[@id="AutoNumber93"]//td[contains(text(), "Average per task")]/following-sibling::td/text()').re(number_re))
        user.add_value('basic_campaigns', hxs.xpath('//table[@id="AutoNumber95"]//td[contains(b/text(), "Basic Campaigns")]/following-sibling::td/b/text()').re(number_re))
        user.add_value('basic_tasks_paid', hxs.xpath('(//table[@id="AutoNumber95"]//td[contains(text(), "Tasks paid")])[1]/following-sibling::td/text()').re(number_re))
        user.add_value('basic_total_paid', hxs.xpath('(//table[@id="AutoNumber95"]//td[contains(text(), "Total paid")])[1]/following-sibling::td/text()').extract())
        user.add_value('hg_campaigns', hxs.xpath('//table[@id="AutoNumber95"]//td[contains(b/text(), "Hire Group")]/following-sibling::td/b/text()').re(number_re))
        user.add_value('hg_tasks_paid', hxs.xpath('(//table[@id="AutoNumber95"]//td[contains(text(), "Tasks paid")])[2]/following-sibling::td/text()').re(number_re))
        user.add_value('hg_total_paid', hxs.xpath('(//table[@id="AutoNumber95"]//td[contains(text(), "Total paid")])[2]/following-sibling::td/text()').extract())
        user.add_value('employer_type', hxs.xpath('//table[@id="AutoNumber95"]//td[contains(b/text(), "Employer type")]/following-sibling::td/text()').re(some_txt_re))
        yield user.load_item()
