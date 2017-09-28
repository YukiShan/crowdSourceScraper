#!/bin/sh

export TERM=xterm-256color

clear

echo 

# echo "Hi, $USER!"

# echo

# echo "Starting crawling rapidworkers.com amazon microtasks..."

cd $HOME/Documents/Research/crowdsourceScraper/scraper

/usr/local/bin/scrapy crawl rapidworkers

/usr/local/bin/scrapy crawl microworkers

cd $HOME/Documents/Research/crowdsourceScraper/appleMeta/appleMeta

/usr/local/bin/scrapy crawl appMeta

echo
