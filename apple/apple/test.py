import logging 


maxdepth = 4 
requrl = 'https://itunes.apple.com/us/rss/customerreviews/page=1/id=606757269/sortBy=mostRecent/xml'

logger.warning('Ignoring link (depth > %d): %s ', maxdepth, requrl)
