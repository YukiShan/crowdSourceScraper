#!/bin/sh

echo "Consolidating JSONs and tar.gz'ing them"
ARCHIVE_FILE=crawl_`date +"%Y-%m-%d-%H-%M"`.tar.gz
./compress_repr.py --delete-original | tar --use-compress-program pigz -cvf $ARCHIVE_FILE -T - --null --remove-files
chmod a-wx $ARCHIVE_FILE

echo "Moving tar.gz's into ~/chev"
DEST_DIR=~/chev/crowdsourcescraper/io/
mkdir -p $DEST_DIR
mv $ARCHIVE_FILE $DEST_DIR 
