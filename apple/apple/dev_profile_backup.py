paginates = hxs.xpath('//body//ul[@class="list paginate"]')
				if paginates:
					global more_app_ids	
					more_app_ids = []				
					curiPhonePage = 1
					curiPadPage = 1
					noiPhonePages = len(paginates.xpath('.//a[contains(@href, "#iPhoneSoftwarePage")]'))
					noiPadPages = len(paginates.xpath('.//a[contains(@href, "#iPadSoftwarePage")]'))
					if noiPhonePages:
						while curiPhonePage < noiPhonePages:		
							curiPhonePage = curiPhonePage + 1
							yield Request(_dev_profile_url(response.meta['id'],curiPhonePage,1), callback=self.parse_dev_successor_page
										  ,meta={'id': response.meta['id'], 'type': APP_TYPE, 'page': curiPhonePage})

					if noiPadPages:
						while curiPadPage < noiPadPages:
							curiPadPage = curiPadPage + 1
							yield Request(_dev_profile_url(response.meta['id'],1,curiPadPage), callback=self.parse_dev_successor_page
										  ,meta={'id': response.meta['id'], 'type': APP_TYPE, 'page': curiPadPage})
							# more_app_ids.append(more_iPadApp_ids)

				more_app_ids = list(set(more_app_ids))				
				app_ids = app_ids + more_app_ids
				developer.add_value('nApps_developed', len(app_ids))				
				developer.add_value('app_ids', app_ids)
				yield developer.load_item()

				# for app_id in app_ids:
				# 	yield self._item_info_request(str(app_id), APP_TYPE, referrer=response.meta['id'])	
				
		def parse_dev_successor_page(self, response):
				"""
				Parses apps developed by the same developer in app store
				"""
			
				self.logger.info('Parsing apps by the same developer: %s  p%d' % (response.meta['id'], response.meta['page']))
				hxs = Selector(response)
				# print(">>>>>>>test here 6666 <<<<<<<<<<<")
				# print(response.url)				
				# parse_app_type = response.meta['flag']
				# apps = []
				# if parse_app_type == 'iPhone':
				# 	apps = hxs.xpath('//body//div[@metrics-loc="Titledbox_iPhone Apps"]//a[@class="artwork-link"]/@href').re(app_id_re)
				# else:
				# 	apps = hxs.xpath('//body//div[@metrics-loc="Titledbox_iPad Apps"]//a[@class="artwork-link"]/@href').re(app_id_re)
				apps = hxs.xpath('//body//a[@class="artwork-link"]/@href').re(app_id_re)
				more_app_ids.append(apps)
				print(">>>>>>>test here 7777 <<<<<<<<<<<")
				print(more_app_ids)
