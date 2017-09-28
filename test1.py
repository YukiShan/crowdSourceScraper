import re

amazonUrls = [u'Need ONLY PEOPLE FROM USA! https://www.amazon.com/dp/B01IKIDBO0/?ref_=aga_p_pl_ln-l_title#customerReviews', u'1. Visit this link and get a free copy of the book: www.amazon.co.uk/dp/B00TPRVW5G', u'2. Open the book and go till the end of the book.\r\nwww.amazon.co.uk/dp/B00TYTYPEA']
amazonUrls_re = re.compile(r'(?:((https?://)?[\w\d?./=_-]+))')
product_id_re = re.compile(r'(?:(?:/dp/)(\w+))')
product_url_id_re = re.compile(r'(?:(?:/gp/product/)|(?:/gp/product/glance/)|(?:/dp/))(\w+)')
review_id_re = re.compile(r'(?:(?:/review/)(\w+))')
url_re = re.compile(r'(?:(?:goo.gl/)([\w/]+))')
sources = 'goo.gl/E5478irdfu/dfehwr'

sthTest = ": 235"
sth_re = re.compile(r'(?:(:))\s\d+')
# urlsList = []
# print(url_re.findall(sources))

# nReviews = "1 customer review"
# number_digit_grpd = re.compile(r'\d+(?:,\d+)*')

# if number_digit_grpd.findall(nReviews):
# 	print(number_digit_grpd.findall(nReviews))
# 	
for item in amazonUrls:
	if amazonUrls_re.findall(item):
		resultUrls = amazonUrls_re.findall(item)
		for url in resultUrls:
			if url[0].find("/") != -1:	
			   print(url[0])			
# 				if product_url_id_re.findall(url[0]):									
# 					prodIds = product_url_id_re.findall(url[0])	
# 					print(">>>>>>>>>4444444444<<<<<<<<<<")
# 					print(prodIds[0])
# 					continue
# 					# for prodId in prodIds:
# 					# 	print(prodIds[0])
# 				    # continue
# 				if review_id_re.findall(url[0]):					
# 					rvwIds = review_id_re.findall(url[0])
# 					print(">>>>>>>>>333333333<<<<<<<<<<")
# 					print(rvwIds[0])
					# for rvwId in rvwIds:
					# 	
				 #        print(rvwIds[0])				
				# for prodId in prodIds:
				# 	# urlsList.append(prodId[0])
				#     print(prodId[0])

# print(">>>>>>>>>>>><<<<<<<<<<<<")
# print(urlsList)