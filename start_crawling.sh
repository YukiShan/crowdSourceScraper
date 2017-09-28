#!/bin/sh

LOG_DIR=log
mkdir -p $LOG_DIR
echo "Starting crawlers in the background"
echo "Writing output to $LOG_DIR dir"
for spider in `scrapy list`
do
  echo "Starting $spider"
  scrapy crawl $spider -s LOG_FILE=./${LOG_DIR}/${spider}_crawl.log &
  # sleep so socket issue won't happen in Twisted when all spiders start at the same time
  sleep 0.1                           
done
