#!/NOBACKUP/scratch/dmei19/anaconda3/bin/python

# some handy functions

import pickle
import time
import sys

def pickle_dump(dict2dump, dict_name):
    pickle_name = dict_name + '.pickle'
    with open(pickle_name, 'wb') as handle:
        pickle.dump(dict2dump, handle, protocol = pickle.HIGHEST_PROTOCOL)
    return pickle_name

def pickle_load(dict_name):
    pickle_name = dict_name + '.pickle'
    with open(pickle_name, 'rb') as handle:
        return pickle.load(handle)
    
def show_tables(con):
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return cur.fetchall()

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

from azure.cognitiveservices.search.websearch import WebSearchAPI
from msrest.authentication import CognitiveServicesCredentials
import json

def simple_bing_search(search_word):
    subscription_key = "" # input key from Bing search
    assert subscription_key
    client = WebSearchAPI(CognitiveServicesCredentials(subscription_key))
    web_data_raw = client.web.search(query=search_word, raw = True, count = 50)
    raw_text = web_data_raw.response.text
    raw_dict = json.loads(raw_text)
    return raw_dict

def print_log(message, logfile = '', mode = 'a'):
    if logfile != '':
        with open(logfile, mode) as f:
            print(message, file = f)
    else:
        print(message, file = sys.stdout)
    return None