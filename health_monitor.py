# -*- coding: utf-8 -*-
"""
Created on Sun Oct 17 16:35:09 2021

@author: jkuhnsman
"""

import requests
import re
import boto3
import time
from datetime import datetime as dt
from datetime import timedelta


url = "http://155.138.239.20:7935/metrics"

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

#%%
    
if __name__ == "__main__":
healthy = True
    
    while True:
        metrics = getMetrics(url)
        if 'livepeer_transcoders_capacity' in metrics.keys():
            print(metrics['livepeer_transcoders_capacity'])
            if int(metrics['livepeer_transcoders_capacity']) > 0:
                healthy = True
            else:
                healthy = False
        else:
            healthy=False
             
        f = open("/root/http/index.html", "w")
        if healthy:    
            f.write("healthy - frankfurt orch")
        else:
            f.write("orch is down - frankfurt orch")
        f.close()
        
        time.sleep(5)
    
