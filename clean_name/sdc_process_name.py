# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 16:33:37 2019

@author: danie
"""

import my_own_handy_functions as mf
import re
import json
import pandas as pd
import time

logfile = ''    

t1 = time.time()

df = pd.read_stata('../../../MA_Feb27/step3_new_ma_all_acq_public.dta') # M&A file
df = df.loc[df['divestiture']=="N"]
df = df.loc[~(df['targetname'].str.contains('Undisclosed', regex=False))] # delete undisclosed target

list_dealnumber = list(df['dealnumber'])
list_targetcusip = list(df['targetcusip'])
list_targetname = list(df['targetname'])

######## delete all things in (), in SDC, the content within () is usually the immediate parent.
######## including it doesn't seem to yield good search results
bracket_re = re.compile(r"\(.*\)")
list_targetname_new = []
for i in range(0,len(list_targetname)):
    name = list_targetname[i]
    if re.search(bracket_re, name):
        newname = bracket_re.sub("",name)
        print(name)
        print(newname)
        list_targetname_new.append(newname)
    else:
        list_targetname_new.append(name)
#################################################        

# dict_replace gives the correct char to replace the old one
with open('dict_char_replace.json', 'r') as f:
    dict_replace = json.load(f)


for i in range(0, len(list_targetname_new)):
    newname = list_targetname_new[i].lower()
    list_targetname_new[i] = newname

####### clean every char to correct one ##############
list_targetname_afcharc = []
for i in range(0, len(list_targetname_new)):
    name = list_targetname_new[i]
    newchar_list = []
    for char in name:
        if char != ' ':
            newchar_list.append(dict_replace[char])
        else:
            newchar_list.append(' ')
    newname = ''.join(newchar for newchar in newchar_list)
    list_targetname_afcharc.append(newname)    
###########################################################   

### process dot carefully, because of .com and .net
dot2replace_re = re.compile(r"(\. )|\.$|^\.") # dot space or dot at the end of the string or dot at beg
for i in range(0, len(list_targetname_afcharc)):
    name = list_targetname_afcharc[i]
    newname = dot2replace_re.sub(' ', name)
    list_targetname_afcharc[i] = newname 

white0 = r" +" # >=1 whitespace 
white0_re = re.compile(white0)
for i in range(0, len(list_targetname_afcharc)):
    name = list_targetname_afcharc[i]
    newname = white0_re.sub(' ', name)
    list_targetname_afcharc[i] = newname

white1 = r"^ | $" # begin or end with whitespace
white1_re = re.compile(white1)
for i in range(0, len(list_targetname_afcharc)):
    name = list_targetname_afcharc[i]
    newname = white1_re.sub('',name)
    list_targetname_afcharc[i] = newname

# take care of u s, u s a
usa_re = re.compile(r"\b(u) \b(s) \b(a)\b")
us_re = re.compile(r"\b(u) \b(s)\b")
for i in range(0, len(list_targetname_afcharc)):
    name = list_targetname_afcharc[i]
    newname = usa_re.sub('usa', name)
    newname = us_re.sub('us', newname)
    list_targetname_afcharc[i] = newname
    
mf.pickle_dump(list_dealnumber, 'ma_acq_public_dealnumber')
mf.pickle_dump(list_targetname_afcharc, 'ma_acq_public_targetname_processed')
