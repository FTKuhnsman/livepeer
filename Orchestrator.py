# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 16:13:26 2021

@author: jkuhnsman
"""

import requests
import re
import boto3
import time
from datetime import datetime as dt
from datetime import timedelta
import socket

class OrchestratorPool():
    def __init__(self):
        self.ec2 = boto3.resource('ec2')
        self.physicalOrchestrators = []
        self.virtualOrchestrators = []
        
    def process_request(self, req):
        print(repr(req))
        
        if req != {}:
            if req['command'] == 'register_orchestrator': self.register_orchestrator(req)
            if req['command'] == 'update_metrics': self.update_metrics(req)
            if req['command'] == 'unregister': self.unregister_orchestrator(req)
        else:
            print('empty request')
    
    def register_orchestrator(self,data):
        print('register orchestrator')
        print(data['type'])
        
        if data['type'] == 'physical':
            orch = Orchestrator(data['ipAddr'],data['type'],data['isDefault'],data['maxSessions'])
            self.physicalOrchestrators.append(orch)
        elif data['type'] == 'virtual':
            orch = VirtualOrchestrator(data['ipAddr'],data['type'],data['maxSessions'],ec2=self.ec2,t_id=data['t_id'])
            self.virtualOrchestrators.append(orch)
        else:
            print('invalid orchestrator type')
    
    def unregister_orchestrator(self,data):
        for orch in self.physicalOrchestrators:
            if orch.ipAddr == data['ipAddr']:
                self.physicalOrchestrators.remove(orch)
        
        for orch in self.virtualOrchestrators:
            if orch.ipAddr == data['ipAddr']:
                self.physicalOrchestrators.remove(orch)
    
    def update_metrics(self, data):
        for orch in self.physicalOrchestrators:
            if orch.ipAddr == data['ipAddr']:
                orch.metrics = data['metrics']
        
        for orch in self.virtualOrchestrators:
            if orch.ipAddr == data['ipAddr']:
                orch.metrics = data['metrics']
                
    def get_available_orchs(self):
        available_orchs = []
        
        for i, orch in enumerate(self.physicalOrchestrators):
            maxSessions = orch.metrics['maxSessions']
            currentSessions = orch.metrics['currentSessions']
            if orch.isDefault == 'yes':
                if maxSessions > 0 and currentSessions < maxSessions:
                    available_orchs.append(orch)           

        for i, orch in enumerate(self.physicalOrchestrators):
            maxSessions = orch.metrics['maxSessions']
            currentSessions = orch.metrics['currentSessions']
            if maxSessions > 0 and currentSessions < maxSessions and orch.isDefault != 'yes':
                available_orchs.append(orch)
                
        for i, orch in enumerate(self.virtualOrchestrators):
            maxSessions = orch.metrics['maxSessions']
            currentSessions = orch.metrics['currentSessions']
            if maxSessions > 0 and currentSessions < maxSessions:
                available_orchs.append(orch)
                
        return available_orchs
                
                
class Orchestrator():
    
    def __init__(self,_ipAddr, _type, _isDefault, _maxSessions):
        self.ipAddr = _ipAddr
        self.metricsUrl = 'http://{}:7935/metrics'.format(self.ipAddr)
        self.type = _type
        self.isDefault = _isDefault
        self.metrics = {
            'maxSessions':_maxSessions,
            'currentSessions':0
            }
    

class VirtualOrchestrator(Orchestrator):
    def __init__(self,_ipAddr, _type, _maxSessions, _isDefault=None, ec2=None,t_id=None):
        Orchestrator.__init__(self, _ipAddr, _type, _isDefault, _maxSessions)
        self.ipAddr = _ipAddr
        self.metricsUrl = 'http://{}:7935/metrics'.format(self.ipAddr)
        self.ec2 = ec2
        self.instance = ec2.Instance(t_id)
        self.min_uptime = 300
        self.t_id = t_id
        self.start_time = dt.now()
        self.min_stop_time = dt.now()
        self.seconds_transcoded = 0.0
        self.type = _type
        self.isDefault = _isDefault
        if ec2 != None:
            self.is_ec2 = True
        else:
            self.is_ec2 = False
    
    def refresh_instance(self):
        self.instance = self.ec2.Instance(self.t_id)
        
    def start(self):
        self.refresh_instance()
        if self.state['Name'] == 'stopped':
            self.instance.start()
            self.start_time = dt.now()
        else:
            print('cannot start. instance {} is currently running'.format(self.t_id))
        
    def stop(self):
        self.refresh_instance()
        print('attempt to stop instance {}'.format(self.t_id))
        state = self.instance.state
        if state['Name'] == 'stopped':
            print('instance {} is not running. no need to stop it')
        else:
            self.instance.stop()
            print('instance {} is stopping'.format(self.t_id))
            
    def attempt_stop(self):
        check_uptime = False
        check_min_stop_time = False
        check_streams = False
        print('total uptime is {} seconds'.format(str(self.uptime)))
        
        if self.uptime < self.min_uptime:
            print('{} has not reached minimum uptime. cannot stop. try again later'.format(self.t_id))
        else:
            check_uptime = True
            
        if dt.now() < self.min_stop_time:
            delta = self.min_stop_time - dt.now()
            print('{} minimum stop time has not been reached. {} seconds remain. try again later'.format(self.t_id,str(delta.seconds)))
        else:
            check_min_stop_time = True
        
        try:
            metrics = getMetrics(self.metricsUrl)
            if 'livepeer_transcode_time_seconds_count' in metrics.keys():
                sec_t = metrics['livepeer_transcode_time_seconds_count']
                print(sec_t)
                if float(sec_t) > self.seconds_transcoded:
                    print('transcoder is still transcoding')
                    self.seconds_transcoded = sec_t
                else:
                    check_streams = True
        except:
            print('cannot get metrics')
        
        if check_uptime & check_min_stop_time & check_streams:
            self.stop()
    
    def reset_min_stop_time(self,seconds):
        self.min_stop_time = dt.now() + timedelta(0,seconds)
        print('reset minimum stop timer {} seconds from now'.format(str(seconds)))
    
    @property
    def state(self):
        self.refresh_instance()
        return self.instance.state
    
    @property
    def uptime(self):
        if self.state['Name'] == 'stopped':
            #print('instance {} is not running'.format(self.t_id))
            return 0
        else:
            delta = dt.now() - self.start_time
            return delta.seconds

url = "http://localhost:7935/metrics"

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
    ec2 = boto3.resource('ec2')
    t1 = Transcoder(ec2,'i-014c83a7f386f9e6b','http://54.156.15.106:7935/metrics')
    t2 = Transcoder(ec2,'i-00c4e3933efe16cae','http://34.194.86.135:7935/metrics')
    
    while True:
        metrics = getMetrics(url)
        if 'livepeer_current_sessions_total' in metrics.keys():
            print(metrics['livepeer_current_sessions_total'])
            
            with open('thresh.txt') as f:
                t = f.read()
            f.close()
            ts = t.split('\n')
            
            if metrics['livepeer_current_sessions_total'] > int(ts[0]):
                t1.reset_min_stop_time(30)
                if t1.state['Name'] == 'stopped':
                    t1.start()
            if metrics['livepeer_current_sessions_total'] > int(ts[1]):
                t2.reset_min_stop_time(30)
                if t2.state['Name'] == 'stopped':
                    t2.start()

        time.sleep(3)
        
        if t1.state['Name'] == 'running':
            t1.attempt_stop()
        if t2.state['Name'] == 'running':
            t2.attempt_stop()
