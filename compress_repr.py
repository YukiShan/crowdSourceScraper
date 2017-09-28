#!/usr/bin/env python
import argparse
from os import listdir
import os
from os.path import isfile, isdir, join
import json
import logging
from datetime import datetime
from scrapy.conf import settings
from sys import stdout


__author__ = 'Shanshan'
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s', datefmt='%H:%M:%S')


def json_default_with_datetime(obj):
        if isinstance(obj, datetime):
            return obj.strftime(settings.get('TS_FMT'))


def compress_repr(data_files, out_file, delete_orig=False):
    if len(data_files) == 0:
        return

    logging.info('Consolidating %d file(s)' % len(data_files))
    items = {}
    for f_path in data_files:
        with open(f_path, 'r') as f:
            for line in f:
                d = json.loads(line)
                id = d['id']
                ts = datetime.strptime(d['timestamp'], settings.get('TS_FMT'))
                del d['id']
                del d['timestamp']
                if id not in items:
                    items[id] = []
                items[id].append((ts, d))

    # sort on timestamp
    logging.debug('Sorting by timestamp')
    for j in items:
        items[j].sort(key=lambda x: x[0])

    logging.debug('Compressing representation')
    for v_list in items.values():
        old_d = v_list[0][1].copy()
        for v in v_list[1:]:
            ts, d = v
            rm_lst = []
            for k in d:
                if k in old_d and d[k] == old_d[k]:
                    rm_lst.append(k)
                else:
                    old_d[k] = d[k]
            for k in rm_lst:
                del d[k]

    logging.debug('Writing output file, one json per line')
    with open(out_file, 'w') as f:
        for j in items:
            f.write(json.dumps({j: items[j]}, separators=(',', ':'), default=json_default_with_datetime) + '\n')
    # Writing the list of output files so other tools like tar can use it
    stdout.write(out_file + '\n')

    if delete_orig:
        logging.info('Deleting originals')
        for f in data_files:
            os.remove(f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compress multiple JSONs of snapshots created by spiders into one json')
    parser.add_argument('--delete-original', default=False, action='store_true', help='Delete original json files (default: %(default)s)')
    parser.add_argument('--io-dir', default='io/', help='Path to the io directory created by the crawler (default: %(default)s)')
    parser.add_argument('--item-types', nargs='+', default=['job', 'user'], help='Item types whose json files are to be consolidated (default: %(default)s)')
    args = parser.parse_args()

    io_dir = args.io_dir
    for spider in listdir(io_dir):
        if not isdir(join(io_dir, spider)):
            continue
        spider_path = join(io_dir, spider)
        for item_type in args.item_types:
            data_files = [join(spider_path, f) for f in listdir(spider_path) if isfile(join(spider_path, f))
                                                                                and f.startswith(item_type)
                                                                                and f.endswith('.json')
                                                                                and not f.endswith('.x.json')]
            data_files.sort(key=lambda f: os.stat(f).st_mtime)
            out_file = join(spider_path, '%s-%s.x.json' % (item_type, datetime.now().strftime(settings.get('TS_FMT'))))
            # skip the most recent file as it might still be being written to
            logging.info('%s::%s' % (spider, item_type))
            compress_repr(data_files[:-1], out_file, delete_orig=args.delete_original)
