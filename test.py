import re

expected = [u'write about thier hotel you stayed in hotel and drunk and slept 1-the first link bad comment \r\n2- second link write good hotel \r\n3- third link write excellent hotel\r\n\r\n1-the first link bad comment\r\n   https://www.tripadvisor.com/UserReviewEdit-g318895-d1202405-e__2F__Hotel__5F__Review__2D__g318895__2D__d1202405__2D__Reviews__2D__Sharah__5F__Mountains__5F__Hotel__2D__Petra__5F__Wadi__5F__Musa__5F__Ma__5F__in__5F__Governorate__2E__html-Sharah_Mountains_Hotel-Petra_Wadi_Musa_Ma_in_Governorate.html']
str1_re = re.compile(r'[Aa]mazon')
s_re = re.compile(r'[Rr]eviews?|[Cc]omments?')
amazon_re = re.compile(r'[Aa][Mm][Aa]?[Zz][Oo]?[Nn]')

app_rvwer_id_re =  re.compile(r'(?:(?:/id))(\w+)')

hasAmazon = False
hasReview = False
for item in expected :
	# print('3333333', item)
	# # print(item)
	# if str1_re.findall(item):
	# 	print('222222', item)
	# 	# print(item)
	# 	hasAmazon = True
	# # results = s_re.findall(item)
	# # # print ("111111", results)
	# # if results:
	# #    print(item)
	# if s_re.findall(item):
	# 	print ("111111", item)
	# 	# print(item)
	# 	hasReview = True
	# if hasAmazon and hasReview:
	# 	print("Found !!")
	# 	break
	if amazon_re.findall(item):
		print ("111111", item)
		# print(item)
		hasReview = True