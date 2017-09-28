import datetime
# from scrapy import log
import scrapy
import logging
from scrapy.http import FormRequest, Request
from scrapy.selector import Selector
from urlparse import urljoin
from scraper.items import MWJob, MWUser
import re
from scrapy.spiders import Spider
from scraper.utils import country_re, number_re, some_txt_re, SingleValItemLoader, only_elem


__author__ = 'Shanshan'

appUrls_re = re.compile(r'(https://[\w\d?./=_-]+)')
xtract_id = re.compile(r'(?<=Id=)\w+')
google_app_id_re = re.compile(r'(?<=id=)[\w.]+')
apple_app_id_re = re.compile(r'(?<=id)\d+')

class MWSpider(Spider):
    name = 'microworkers'
    start_urls = ['https://microworkers.com/login.php']

    def parse(self, response):
        if 'login_attempted' in response.meta:
            # check login succeed before going on
            if "Email and password don't match" in response.body:
                self.logger.debug("Login failed")
                return
            else:
                return Request('https://microworkers.com/jobs.php?Id_category=70&Sort=NEWEST&Filter=no',callback=self.parse_job_list), Request('https://microworkers.com/jobs.php?Id_category=50&Sort=NEWEST&Filter=no',callback=self.parse_job_list)
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
        joblist = hxs.xpath('//body//div[@class="jobslist"]')
        for job in joblist:
            # success percentage is only available on the job list page, so it has to be passed to the task parser as an
            # additional piece of information
            job_success_pct = only_elem(job.xpath('./div[4]//text()').extract()).strip()            
            job_url = only_elem(job.xpath('./div[2]//a/@href').extract())
            if job_url.find('jobs_details') == -1:            
                continue      
            job_url = urljoin('http://microworkers.com/', job_url)      
            # print(">>>>>>>>>>>>>2222222222222", job_url)
            yield Request(job_url, callback=self.parse_single_job, meta={'job_success_pct': job_success_pct})

    def parse_single_job(self, response):
        """
        Parses a single Job and produces MWJob item
        """

        self.logger.debug('Parsing job %s' % response.url)        
        hxs = Selector(response)
        # Abort not running jobs
        if hxs.xpath('//body//td/text()').re('This job is currently not running'):
            self.logger.info('Aborting not-running job %s' % response.url)
            return       
               
        parent_node = hxs.xpath('//body//div[@class="jobarealeft"]')
        assert len(parent_node) == 1
        name = parent_node.xpath('./h1/text()').extract()        
        if ("feedback" not in name[0].lower()) and ("review" not in name[0].lower()) and ("rate" not in name[0].lower()) and ("review/feedback" not in name[0].lower()):
            self.logger.info('Not target job!')
            return
        appWthPaidRvw = False
        expected = parent_node.xpath('./div[@class="jobdetailsbox"]/p[2]/text()').extract()
        for eachTxt in expected:
            if "https://" in eachTxt.lower() and "app" in eachTxt.lower():
                appWthPaidRvw = True
                break
        if not appWthPaidRvw:
            self.logger.info('Not target job!')
            return

        print(">>>>>>>>>>>>>2222222222222", name[0])
        for item in expected:
            if not appUrls_re.findall(item):
                continue
            res_urls = appUrls_re.findall(item)
            assert len(res_urls) == 1
            yield Request(res_urls[0], callback=self.parse_app_url, meta={'url': response.url,
                                                                          'parent_node': parent_node,                                                                          
                                                                          'job_success_pct': response.meta['job_success_pct']})
       

    def parse_app_url(self, response):
        self.logger.info("Scraping app urls")
        settings = self.crawler.settings
        parent_node = response.meta['parent_node']  

        # Fill in the data of the job        
        job = SingleValItemLoader(item=MWJob(), response=response)        
        job.add_value('timestamp', datetime.datetime.now().strftime(settings['TS_FMT']))
        job.add_value('success_pct', response.meta['job_success_pct'])
        job.add_value('url', response.meta['url'])     
        # print(">>>>>>>microworkers jobUrl<<<<<<<<<<")   
        # print(job._values['url'])
        job.add_value('name', parent_node.xpath('./h1/text()').extract())        
        job.add_value('id', parent_node.xpath('.//div[@class="jobdetailsnoteleft"]/p[4]/text()').re(r'Job ID:\s+(\w+)'))
        t = parent_node.xpath('.//div[@class="jobdetailsnoteleft"]/p/strong/text()').re(number_re)
        job.add_value('work_done', t[0])
        job.add_value('payment', t[1])
        job.add_value('duration', t[2]) 
        job.add_value('work_total', parent_node.xpath('.//div[@class="jobdetailsnoteleft"]//sup/text()').re(number_re)[0])       
        href = only_elem(parent_node.xpath('.//div[@class="jobdetailsnoteright"]/p[1]/a/@href').extract())
        job.add_value('employer', xtract_id.search(href).group(0))
        job.add_value('countries', parent_node.xpath('.//div[@class="countrychoise"]/p[2]/text()').re(country_re))
        
        # category = parent_node.xpath('./p[1]//b/text()').re(some_txt_re)[0].split(' (')
        job.add_value('category', parent_node.xpath('./p[1]//b/text()').re(some_txt_re))
        # job.add_value('sub_cat', category[1][:-1])
        if response.url.find('google') != -1:
            job.add_value('app_platform', 'Google Play')
            job.add_value('app_id', google_app_id_re.findall(response.url)[0])    
            # print(">>>>>>>app_platform, app_id<<<<<<<<<<")   
            # print(job._values['app_platform'], job._values['app_id'])     
        else:
            job.add_value('app_platform', 'App store')
            job.add_value('app_id', apple_app_id_re.findall(response.url)[0])  
            # print(">>>>>>>app_platform, app_id<<<<<<<<<<")   
            # print(job._values['app_platform'], job._values['app_id'])           
        job.add_value('expected', parent_node.xpath('./div[@class="jobdetailsbox"]/p[2]/text()').extract())
        job.add_value('proof', parent_node.xpath('./div[@class="jobdetailsbox"]/p[4]/text()').extract())
        yield job.load_item()
        # user_url = urljoin(response.url, href)
        # yield Request(user_url, callback=self.parse_single_user)

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
        user.add_value('name', hxs.xpath('//div[@class="usershortinfoleft"]//label[contains(text(), "Username")]/following-sibling::span//text()').extract())
        user.add_value('id', hxs.xpath('//div[@class="usershortinfoleft"]//label[contains(text(), "ID")]/following-sibling::span/text()').extract())
        user.add_value('member_since', hxs.xpath('//div[@class="usershortinfoleft"]//label[contains(text(), "Member since")]/following-sibling::span/text()').extract())
        user.add_value('country', hxs.xpath('//div[@class="usershortinfoleft"]//label[contains(text(), "Country")]/following-sibling::span/text()').re(some_txt_re))
        user.add_value('city', hxs.xpath('//div[@class="usershortinfoleft"]//label[contains(text(), "City")]/following-sibling::span/text()').re(some_txt_re))
        user.add_value('total_earned', hxs.xpath('//div[@class="workerstatistics"]//label[contains(text(), "Total Earned")]/following-sibling::span/text()').re(number_re))
        user.add_value('tasks_done', hxs.xpath('//div[@class="workerstatistics"]//label[contains(text(), "Tasks done")]/following-sibling::span/text()').re(number_re))
        user.add_value('basic_tasks', hxs.xpath('//div[@class="workerstatistics"]//label[contains(text(), "Basic tasks")]/following-sibling::span/text()').re(number_re))
        user.add_value('basic_satisfied', hxs.xpath('//div[@class="workerstatistics"]/div[@class="staticticscol01"]/div[2]//label[contains(text(), "Satisfied") and not(contains(text(), "Not"))]/following-sibling::span/text()').re(number_re))
        user.add_value('basic_not_satisfied', hxs.xpath('//div[@class="workerstatistics"]/div[@class="staticticscol01"]/div[2]//label[contains(text(), "Not-Satisfied")]/following-sibling::span/text()').re(number_re))
        user.add_value('basic_avg_per_task', hxs.xpath('//div[@class="workerstatistics"]/div[@class="staticticscol01"]/div[2]//label[contains(text(), "Average per task")]/following-sibling::span/text()').re(number_re))
        user.add_value('hg_tasks', hxs.xpath('//div[@class="workerstatistics"]/div[@class="staticticscol01"]/div[3]//label[contains(text(), "Hire Group")]/following-sibling::span/text()').re(number_re))
        user.add_value('hg_satisfied', hxs.xpath('//div[@class="workerstatistics"]/div[@class="staticticscol01"]/div[3]//label[contains(text(), "Satisfied") and not(contains(text(), "Not"))]/following-sibling::span/text()').re(number_re))
        user.add_value('hg_not_satisfied', hxs.xpath('//div[@class="workerstatistics"]/div[@class="staticticscol01"]/div[3]//label[contains(text(), "Not-Satisfied")]/following-sibling::span/text()').re(number_re))
        user.add_value('hg_avg_per_task', hxs.xpath('//div[@class="workerstatistics"]/div[@class="staticticscol01"]/div[3]//label[contains(text(), "Average per task")]/following-sibling::span/text()').re(number_re))
        user.add_value('basic_campaigns', hxs.xpath('//div[@class="employerstatistics"]//label[contains(text(), "Basic Campaigns")]/following-sibling::span/text()').re(number_re))
        user.add_value('basic_tasks_paid', hxs.xpath('(//div[@class="employerstatistics"]//label[contains(text(), "Tasks paid")])[1]/following-sibling::span/text()').re(number_re))
        user.add_value('basic_total_paid', hxs.xpath('(//div[@class="employerstatistics"]//label[contains(text(), "Total paid")])[1]/following-sibling::span/text()').extract())
        user.add_value('hg_campaigns', hxs.xpath('//div[@class="employerstatistics"]//label[contains(text(), "Hire Group")]/following-sibling::span/text()').re(number_re))
        user.add_value('hg_tasks_paid', hxs.xpath('(//div[@class="employerstatistics"]//label[contains(text(), "Tasks paid")])[2]/following-sibling::span/text()').re(number_re))
        user.add_value('hg_total_paid', hxs.xpath('(//div[@class="employerstatistics"]//label[contains(text(), "Total paid")])[2]/following-sibling::span/text()').extract())
        user.add_value('employer_type', hxs.xpath('//div[@class="employerstatistics"]//label[contains(text(), "Employer type")]/following-sibling::span/text()').re(some_txt_re))
        yield user.load_item()
