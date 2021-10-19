# -*- coding: utf-8 -*-
"""
Created on Sun Oct 17 16:35:09 2021

@author: jkuhnsman
"""

import requests
import re
import time
from datetime import datetime as dt
from datetime import timedelta
import subprocess
import sys

url = "http://chicago.ftkuhnsman.com:7935/metrics"

def getMetrics(url):
    r = requests.get(url, verify=False)
    raw = r.text
    raw_split = raw.split('\n')

    metrics = []
    
    for m in raw_split:
        if (not '#' in m) & ('livepeer' in m):
            metrics.append(m)

    metrics_parsed = {}
    
    for m in metrics:
        l = re.split('{|}',m)
        metrics_parsed[l[0]] = float(str(l[-1]).strip())
    
    return metrics_parsed

def restartService():
    try:
        cmd = '/bin/systemctl restart livepeer.service'
        completed = subprocess.run( cmd, shell=True, check=True, stdout=subprocess.PIPE )
    except subprocess.CalledProcessError as err:
            print( 'ERROR:', err )
            
#%%
    
if __name__ == "__main__":
    waiting = True
    
    while waiting:
        metrics = getMetrics(url)
        if 'livepeer_current_sessions_total' in metrics.keys():
            print(metrics['livepeer_current_sessions_total'])
            if int(metrics['livepeer_current_sessions_total']) == 0:
                restartService()
                waiting = False
        else:
        
        time.sleep(5)
    
