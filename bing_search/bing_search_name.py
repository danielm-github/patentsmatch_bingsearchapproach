#!/NOBACKUP/scratch/dmei19/anaconda3/bin/python
# this program runs bing search on Columbia Research Grid
# it runs embarrassingly parallel jobs with multiple tasks 

import pickle
import pandas as pd
import sqlite3
import time
import sys
from azure.cognitiveservices.search.websearch import WebSearchAPI
from msrest.authentication import CognitiveServicesCredentials

subscription_key = "" # insert your Bing key here
assert subscription_key
client = WebSearchAPI(CognitiveServicesCredentials(subscription_key))

client_id = "";
Empty_Search_Word_Err = "Empty Search Word"

#############################################################################
#More details for bing web search please refer to 
#https://docs.microsoft.com/en-us/azure/cognitive-services/bing-web-search/web-sdk-python-quickstart

def bing_web_search_sdk_list(search_word_list, c = 50):
    list_name_url = []
    list_raw = []
    list_urls = []
    for search_word in search_word_list:
        #sanity check to avoid any potential issue
        if len(search_word) == 0 :
            raise Exception(Empty_Search_Word_Err)    
        
        web_data_raw = client.web.search(query=search_word, raw = True, count = c) 
        raw = web_data_raw.response.text
        list_raw.append(raw)
        
        name_url = []
        urls = []
        if hasattr(web_data_raw.output.web_pages, 'value'):        
            for i in web_data_raw.output.web_pages.value:
                name_url.append((i.name, i.url))
                urls.append(i.url) 
        
        list_name_url.append(str(name_url))
        list_urls.append(str(urls))
        
    return list_name_url, list_raw, list_urls
##############################################################################

#beg##########################################################
def log_time_used(t1, task, log, mode = 'a'):
    t2 = time.time()
    t = round(t2-t1,2)
    message = f"{task} takes {t}s."
    if log == '':
        print(message, file = sys.stdout)
    else:
        with open(log, mode) as f:
            print(message, file = f)
    return time.time()
#end############################################################

t_start = time.time()
t1 = time.time()

# insert the processed names from SDC/Compustat/PatentsView
with open('sdc/compustat/patentsview_name.pickle', 'rb') as handle:
    list_name = pickle.load(handle)

# take task no, 1-7 for Compustat, 1-10 for SDC, 1-1000 for PatentsView
task_num = int(sys.argv[1])

logfile = 'search_task' + str(task_num) + '.log'
task_size = 5000 # each task searches 5000 names
task_start = (task_num - 1) * task_size
task_end = min(task_num * task_size, len(list_name))
list_task = list_name[task_start:task_end]

df = pd.DataFrame()
df['newname'] = list_task

# for each task, create a database to store ALL the search results
db = 'search_task' + str(task_num) + '.db'
con = sqlite3.connect(db)
cur = con.cursor()
table = 'newname_task' + str(task_num)
df.to_sql(table, con, if_exists = "replace")

###########################################
def show_tables():
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return cur.fetchall()

def drop_tables(table_name):
    query = str( f"DROP TABLE {table_name}" )
    cur.execute(query)
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return cur.fetchall()
#################################################
    
result_table = 'search_result_task' + str(task_num)
try:
    drop_tables(result_table)
except:
    print('no result table in db yet')    

t1 = log_time_used(t1, 'getting ready', log = logfile, mode = 'w+')

##############################################################################
### for each task of 5000 searches, divide it into 5 batches
# after each batch, store them into the corresponding database
# this is to avoid any break-down of the tasks so that the cost of Bing search is wasted
def batch_search_new(n, s, c = 50):
    
    #############################################
    t1 = time.time()
    
    begin = (n-1)*s
    end = min(n*s, len(list_task))
    name_list = list_task[begin:end]
    list_name_url, list_raw, list_urls = bing_web_search_sdk_list(name_list, c)
            
    df_result = pd.DataFrame()
    df_result['newname'] = name_list
    df_result['name_url'] = list_name_url
    df_result['raw'] = list_raw
    df_result['urls'] = list_urls
    sql_name = 'sdc_search_result_task' + str(task_num)
    df_result.to_sql(sql_name, con, if_exists = 'append')
    
    t1 = log_time_used(t1, f"query + save {s} searches to sql", log = logfile)
    
#####################################################################################

t_start = time.time()
batch_size = 1000 # 5 batches within one task
if len(list_task) % batch_size == 0:
    batch_round = int(len(list_task) / batch_size)
else:
    batch_round = int(len(list_task) / batch_size) + 1

for batch_num in range(1, batch_round+1):
    batch_search_new(batch_num, batch_size)
    if logfile == '':
        # after each batch, print
        print(f"processed batch No. {batch_num}")
    else:
        with open(logfile, 'a') as f:
            print(f"processed batch No. {batch_num}", file = f)
            
t1 = log_time_used(t_start, f"{batch_round} rounds done", log = logfile)

#####validation code
#sql = "select * from sdc_search_result_task1 limit 100;"
#df_temp = pd.read_sql(sql, con)
#print(df_temp)