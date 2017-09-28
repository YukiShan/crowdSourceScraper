import feedparser
import calendar


app_countries = {
    'China':'cn',
    'United States':'us'
}

app_ranklists = {
    'topfreeapplications':'Top Free',
    'toppaidapplications':'Top Paid',
    'topgrossingapplications':'Top Grossing',
    'topfreeipadapplications':'Top Free iPad',
    'toppaidipadapplications':'Top Paid iPad',
    'topgrossingipadapplications':'Top Grossing iPad',
    'topmacapps':'Top Mac Apps'
}

app_genres = {
    'None':None,
    'Books':'6018',
    'Business':'6000',
    'Catalogs':'6022',
    'Education':'6017',
    'Entertainment':'6016',
    'Finance':'6015',
    'Food & Drink':'6023',
    'Games':'6014',
    'Health & Fitness':'6013',
    'Lifestyle':'6012',
    'Medical':'6020',
    'Music':'6011',
    'Navigation':'6010',
    'News':'6009',
    'Newsstand':'6021',
    'Photo & Video':'6008',
    'Productivity':'6007',
    'Reference':'6006',
    'Social Networking':'6005',
    'Sports':'6004',
    'Travel':'6003',
    'Utility':'6002',
    'Weather':'6001'
}

def mk_rssfeed(country_code, rank_list, genre_code=None, limit=200):
    """
    country_code short name of country, eg, cn, us
    rank_list rank list name, eg, topfreeapplications
    genre_code app category code, eg, Sports=
    """
    rss_feed_parts = []
    rss_feed_parts.append('https://itunes.apple.com')
    rss_feed_parts.append(country_code)
    rss_feed_parts.append('rss')
    rss_feed_parts.append(rank_list)
    rss_feed_parts.append('limit=%d' % limit)
    if genre_code != None:
        rss_feed_parts.append('genre=' + genre_code)
    rss_feed_parts.append('xml')
    return ('/').join(rss_feed_parts)


def parse_feed(url):    
    feed = feedparser.parse(url)  
    rank_list = []
    rank = 0
    for item in feed.entries:        
        rank += 1
        link = item['id']
        rank_list.append({'rank':rank,
                          'id':link[link.find('/id')+3:link.find('?mt')],
                          'title':item['title'],
                          'link':link,
                          'timestamp':calendar.timegm(item['updated_parsed'])})    
    return rank_list 


def get_app_rank(app_id, country_code, rank_item, app_genre_code=None):  
    rank_map = {} 
    rank_list_name = None
    feed_url = mk_rssfeed(country_code, rank_item, app_genre_code)
    rank_list = parse_feed(feed_url)

    for item in rank_list:    
        if app_id == item['id']: 
            rank_map = item     
            rank_list_name = app_ranklists[rank_item]    
            break    
    return rank_map, rank_list_name


def get_rank(app_id, app_genre_name=None, country_id = app_countries['United States']):
    if not app_genre_name:
        app_genre_code = None
    elif app_genre_name in app_genres:
        app_genre_code = app_genres[app_genre_name]
    else:
        print 'Invalid app genre name'
        return

    for key in app_ranklists:
        rank_map, rank_list_name = get_app_rank(app_id, country_id, key, app_genre_code)
        if rank_map:
            break
    # if not rank_map:
    #     print 'Nothing was found!'
    # else:
    #     print rank_map
    #     print rank_list_name
    return rank_map, rank_list_name


def main():
    get_rank('1111479706','Games')


if __name__ == '__main__':
    main()
    pass
