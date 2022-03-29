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
    
    registered = True
    
    with open('client_config') as f:
        t = f.read()
        f.close()
        ts = t.split('\n')
    
    
    while True:
        try:
            data = {}
            metrics = getMetrics('http://{}:7935/metrics'.format(ts[0]))
            
            if registered:
                if 'livepeer_current_sessions_total' in metrics.keys():
                    print(metrics['livepeer_current_sessions_total'])
                    data['currentSessions'] = metrics['livepeer_current_sessions_total']
                else:
                    data['currentSessions'] = 0.0
                    
                data['maxSessions'] = metrics['livepeer_max_sessions_total']
                print(metrics['livepeer_max_sessions_total'])
                
                r = requests.post('http://{}:{}/'.format(ts[2],ts[3]), json={'command':'update_metrics','ipAddr':ts[1], 'metrics':data})
                if r.status_code == 900:
                    r = requests.post('http://{}:{}/'.format(ts[2],ts[3]), json={'command':'register_orchestrator',
                                                                             'type':ts[4],
                                                                             'ipAddr':ts[1],
                                                                             'maxSessions':metrics['livepeer_max_sessions_total'],
                                                                             'isDefault':ts[5]})
                
            else:
                r = requests.post('http://{}:{}/'.format(ts[2],ts[3]), json={'command':'register_orchestrator',
                                                                             'type':ts[4],
                                                                             'ipAddr':ts[1],
                                                                             'maxSessions':metrics['livepeer_max_sessions_total'],
                                                                             'isDefault':ts[5]})
                
                if r.status_code == 200: registered = True
        except:
            print('orchestrtor is not running')
            try:
                if registered:
                    r = requests.post('http://{}:{}/'.format(ts[2],ts[3]), json={'command':'unregister','ipAddr':ts[1]})
            except:
                pass
            registered = False
            
        time.sleep(1)