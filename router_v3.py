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

import Orchestrator

imp.reload(Orchestrator)

global body
global KEEP_RUNNING
KEEP_RUNNING = True

class Server():
    def __init__(self):
        self.name = None
        self.age = None
        
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
    
    httpd = HTTPServer(('localhost', 80), SimpleHTTPRequestHandler)
    while KEEP_RUNNING:
        httpd.handle_request()
    
    time.sleep(1)
    print('http server is done')
    
def always_on():
    global KEEP_RUNNING
    print('running')
    time.sleep(10)
    print('stopped')
    KEEP_RUNNING = False
    requests.post('http://127.0.0.1:80/', json={})
    
#%%
global orchPool
orchPool = Orchestrator.OrchestratorPool()
#%%
js1 = {'command':'register_orchestrator',
        'type':'physical',
        'ipAddr':'0.0.0.0',
        'maxSessions':'10'}

js2 = {'command':'register_orchestrator',
        'type':'virtual',
        'ipAddr':'0.0.0.0',
        'maxSessions':'10',
        't_id':'i-014c83a7f386f9e6b'}

met = {'command':'update_metrics',
        'ipAddr':'0.0.0.0',
        'metrics':{'maxSessions':10, 'currentSessions':5}
        }

orchPool.register_orchestrator(js1)
orchPool.register_orchestrator(js2)
#%%
if __name__ == "__main__":      
    global KEEP_RUNNING
    KEEP_RUNNING = True
    server_thread = Thread(target=http_server)
    alwayson_thread = Thread(target=always_on)
    #alwayson_thread.setDaemon(True)
    server_thread.start()
    alwayson_thread.start()
    
    #server_thread.join()
    #alwayson_thread.join()
    
    print('done')