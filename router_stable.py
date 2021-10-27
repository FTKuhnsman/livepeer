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
            self.current_orch = orch
            self.iptable_flush()
            self.iptable_add(orch)
    
    def iptable_flush(self):
        iptc.Table('nat').chains[0].flush()
        
    def iptable_add(self,orch):
        add_orch = 'iptables -t nat -A PREROUTING -i enp1s0 -p tcp --dport 8935 -j DNAT --to {}'
        os.system(add_orch.format(orch.ipAddr))
        
    
        
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    global orchPool    
    global server
    
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length)
        data_decoded = data.decode('utf-8')
        body = ast.literal_eval(data_decoded)
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
    global router
    print('clear iptables')
    while True:
        availableOrchs = router.orchPool.get_available_orchs()
        
        if len(availableOrchs) > 0:
            router.set_current_orch(availableOrchs[0])
        else:
            print('no orchestrators available')
            
        time.sleep(3)

global orchPool
orchPool = Orchestrator.OrchestratorPool()

global router
router = Router(orchPool)

if __name__ == "__main__":      
    
    KEEP_RUNNING = True
    server_thread = Thread(target=http_server)
    server_thread.daemon = True
    server_thread.start()
    
    #server_thread.join()
    
    main_thread = Thread(target=main)
    main_thread.start()


        
        
        
        
        
        
        