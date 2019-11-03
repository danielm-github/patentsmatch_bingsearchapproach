# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 16:25:50 2019

@author: danie
"""

import pandas as pd
import sqlite3
import json
import sys

def print_log(message, logfile = '', mode = 'a'):
    if logfile != '':
        with open(logfile, mode) as f:
            print(message, file = f)
    else:
        print(message, file = sys.stdout)
    return None

#prefix = 'compustat_'
#prefix = 'pv_'
prefix = 'sdc_'
logfile = ''

attach_sql = ";"
attach_name = ""

suffix = 'all'

db_folder = f"../../../Apps/CBS_ResearchGrid/{prefix}search_result_db/"
db = db_folder + f"{prefix}search_{suffix}.db"
con = sqlite3.connect(db)
cur = con.cursor
sql = f"select * from {prefix}search_result_" + suffix + attach_sql
df = pd.read_sql(sql, con)
try:
    df = df.drop('index', 1)
except:
    pass

con.close()

print_log('data load done', logfile, 'w+')

list_urls = []
list_names = []
list_newname = list(df['newname'])
list_raw = list(df['raw'])

for obs in range(0, len(list_newname)):
    urls = []
    names = []
    item = list_raw[obs]
    newname = list_newname[obs]
    dict_item = json.loads(item)
    if 'webPages' not in dict_item:
        print_log(f"{obs} does not have webpage result", logfile)
        print_log(newname, logfile)
    else:
        if 'value' in dict_item['webPages']:
            for webpage in dict_item['webPages']['value']:
                urls.append(webpage['url'])
                names.append(webpage['name'])
    list_urls.append(urls)
    list_names.append(names)
    if (obs+1) % 50000 == 0:
        print_log(f"{obs+1} observations processed", logfile)

print_log("start to pick top 5", logfile)

list_urls5 = []
list_names5 = [] 
for obs in range(0, len(list_newname)):
    urls = list_urls[obs]
    names = list_names[obs]
    top5 = min(5, len(urls), len(names))
    urls5 = urls[0:top5]
    names5 = names[0:top5]
    list_urls5.append(str(urls5))
    list_names5.append(str(names5))

print_log("start saving to sql", logfile)

df_result = pd.DataFrame()
df_result['newname'] = list_newname
df_result['urls5'] = list_urls5
df_result['names5'] = list_names5

db = db_folder + f"{prefix}search_{suffix}_top5.db"
con = sqlite3.connect(db)
cur = con.cursor

table = f"{prefix}search_{suffix}_top5"
df_result.to_sql(table, con, if_exists = "replace")
con.close()

print_log("all done", logfile)

## validation code
con = sqlite3.connect(db)
sql = 'select * from ' + table + ' limit 10;'
df_test = pd.read_sql(sql, con)
try:
    df_test = df_test.drop('index', 1)
except:
    pass
con.close()
with open(f"{prefix}test.out", 'w+', encoding='utf-8') as f:
    print(df_test, file=f)

