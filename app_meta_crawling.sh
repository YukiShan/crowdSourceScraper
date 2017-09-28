#!/bin/sh

export TERM=xterm-256color

clear

echo 


cd $HOME/Documents/Research/crowdsourceScraper/apple/apple

/usr/local/bin/scrapy crawl appReviews

echo
