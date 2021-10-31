# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 17:47:10 2021

@author: jkuhnsman
"""
import requests
import re
import time
import functools
print = functools.partial(print, flush=True)

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
    
    with open('client_config') as f:
        t = f.read()
        f.close()
        ts = t.split('\n')
    
 
        r = requests.post('http://{}:{}/'.format(ts[2],ts[3]), json={'command':'register_orchestrator',
                                                                 'type':ts[4],
                                                                 'ipAddr':ts[1],
                                                                 'maxSessions':metrics['livepeer_max_sessions_total'],
                                                                 'isDefault':ts[5]})