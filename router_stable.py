# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 12:00:29 2021

@author: jkuhnsman
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import json
import ast
from threading import Thread
import time
import requests
import imp
import os
import iptc
import sys
import functools
print = functools.partial(print, flush=True)

import Orchestrator

imp.reload(Orchestrator)

global body
global KEEP_RUNNING
KEEP_RUNNING = True

class Router():
    def __init__(self, _orchPool):
        self.orchPool = _orchPool
        self.current_orch = None
    
    def orchPoolHasPhysicalOrchs(self):
        if len(self.orchPool.physicalOrchestrators) > 0:
            return True
        else:
            return False
        
    def set_current_orch(self, orch):
        if self.current_orch == orch:
            print('already using the best orchestrator')
        else:
            if self.current_orch != None: self.iptable_drop(self.current_orch)
            self.iptable_add(orch)
            self.current_orch = orch
    
    def iptable_flush(self):
        table = iptc.Table('nat')
        chain = iptc.Chain(table,'PREROUTING')
        chain.flush()
    
    def iptable_drop(self,orch):
        drop_orch = 'iptables -t nat -D PREROUTING -i enp1s0 -p tcp --dport 8935 -j DNAT --to {}'
        os.system(drop_orch.format(orch.ipAddr))
        print('flush iptables')
        
    def iptable_add(self,orch):
        add_orch = 'iptables -t nat -A PREROUTING -i enp1s0 -p tcp --dport 8935 -j DNAT --to {}'
        os.system(add_orch.format(orch.ipAddr))
        print('add orch to iptables')
        
    
        
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    global orchPool    
    global server
    global router
    
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)
        data_decoded = data.decode('utf-8')
        body = ast.literal_eval(data_decoded)
        if body['command'] == 'update_metrics' and not body['ipAddr'] in router.orchPool.orch_ips:
            self.send_response(900)
        else:
            self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        response.write(data)
        self.wfile.write(response.getvalue())
        #print(repr(body))
        orchPool.process_request(body)
        
def http_server():
    #global server
    global KEEP_RUNNING
    
    httpd = HTTPServer(('', 6000), SimpleHTTPRequestHandler)
    while True:
        httpd.handle_request()
    
    time.sleep(1)
    print('http server is done')
    
def main():
    print('start router')
    global router
    router.iptable_flush()
    while True:
        availableOrchs = router.orchPool.get_available_orchs()
        print("Available Orchestrators")
        for o in availableOrchs:
            print("IP - {};  MaxSessions - {};  CurrentSessions - {}".format(o.ipAddr, o.metrics['maxSessions'], o.metrics['currentSessions']))
        
        if len(availableOrchs) > 0:
            router.set_current_orch(availableOrchs[0])
            print('set current orchestrator')
        else:
            print('no orchestrators available')
            
        time.sleep(1)

global orchPool
print('create orch pool')
orchPool = Orchestrator.OrchestratorPool()

global router
print('create router')
router = Router(orchPool)

if __name__ == "__main__":      
    
    KEEP_RUNNING = True
    server_thread = Thread(target=http_server)
    server_thread.daemon = True
    server_thread.start()
    
    #server_thread.join()
    
    main_thread = Thread(target=main)
    main_thread.start()


        
        
        
        
        
        
        