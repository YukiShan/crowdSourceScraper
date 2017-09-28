import re 

appUrls_re = re.compile(r'(https://[\w\d?./=_-]+)')

strgoal= 'Sign up'

# print appUrls_re.findall(strgoal)
if not appUrls_re.findall(strgoal):
	print 'yes'