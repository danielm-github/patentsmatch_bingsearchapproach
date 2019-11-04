#!/NOBACKUP/scratch/dmei19/anaconda3/bin/python

import pandas as pd
import sqlite3


attach_sql = ";"
attach_name = ""

num_task = 10 # 7 for Compustat / 10 for SDC / 100 for PatentsView
df_list = [None] * num_task

#prefix = 'compustat'
#prefix = 'pv'
prefix = 'sdc'
db_folder = prefix + '_search_result_db/'

for i in range(1, num_task+1):
    db = db_folder + prefix + '_search_task' + str(i) + '.db'
    con = sqlite3.connect(db)
    cur = con.cursor
    sql = f"select * from {prefix}_search_result_task" + str(i) + attach_sql
    df = pd.read_sql(sql, con)
    df = df.drop('index', 1)
    df_list[i-1] = df
    con.close()

print('save list done')

db = db_folder + prefix + '_search_all' + attach_name + '.db'
con = sqlite3.connect(db)
for i in range(0, len(df_list)):
    dataframe = df_list[i]
    table_name = prefix + '_search_result_all' + attach_name
    if i == 0:
        dataframe.to_sql(table_name, con, if_exists='replace', index = False)
    else:
        dataframe.to_sql(table_name, con, if_exists='append', index = False)
    print(str(i+1) + ' tables processed')

query = f"select * from {prefix}_search_result_all limit 100;"
df_sample = pd.read_sql(query, con)
print(df_sample)

con.close()
