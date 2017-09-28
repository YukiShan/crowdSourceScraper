from os import listdir, chdir
from os.path import isfile, join
import json
import logging
from datetime import datetime

logging.root.setLevel(logging.INFO)
chdir('D:\\Users\\Amir\\PycharmProjects\\CrowdSourceScraper')

io_dir = 'io\\microworkers'
data_files = [ join(io_dir, f) for f in listdir(io_dir) if isfile(join(io_dir,f)) and f.startswith('job') and f.endswith('.json') ]

jobs = {}

for f_path in data_files:
    with open(f_path, 'r') as f:
        for line in f:
            d = json.loads(line)
            id = d['id']
            ts = datetime.strptime(d['timestamp'], "%Y-%m-%d %H:%M:%S")
            del d['id']
            del d['timestamp']
            d['work_done'] = int(d['work_done'])
            d['work_total'] = int(d['work_total'])
            d['duration'] = int(d['duration'])
            if 'success_pct' in d:
                if d['success_pct'] and d['success_pct'] != 'N/A':
                    d['success_pct'] = float(d['success_pct'])
                else:
                    del d['success_pct']
            if id not in jobs:
                jobs[id] = []
            jobs[id].append((ts, d))
        logging.info('read %s' % f_path)

# sort on timestamp
logging.info('sorting by timestamp')
for j in jobs:
    jobs[j].sort(key=lambda x: x[0])

logging.info('compressing representation')
for v_list in jobs.values():
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

## plot jobs work_done
#for j in jobs.values():
#    t = zip(*j)
#    x_s, y_s = t[0], [y['work_done'] for y in t[1]]
#    plot(x_s, y_s, 'o-')
#plt.setp(plt.xticks()[1], rotation=30)

#for j in j_s:
#    data = [(ts, y['work_done']) for ts, y in j if 'work_done' in y]
#    x_s, y_s = zip(*data)
#    plot(x_s, np.array(y_s) - min(y_s), '-')
#    #plot(x_s[-1], y_s[1][-1] - min(y_s[0]), 'o')

j_s = [j for j in jobs.values() if max([v[1]['work_done'] for v in j]) - min([int(v[1]['work_done']) for v in j]) > 0]