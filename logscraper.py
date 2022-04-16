#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 16:35:09 2021
TO DO:
    intermitent issue where 'database locked' error is raised
@author: ghost
"""
import time
import datetime
import subprocess as sub
import json

streams = {'ip':'47.205.87.4', 'streams':{}}


proc1 = sub.Popen(('sudo','tail','-f','/var/log/livepeer/livepeer.log'), stdout=sub.PIPE)
while True:
    byte = proc1.stdout.readline()
    line = byte.decode('utf-8')
    spline = line.split(' ')
    if '.ts' in spline[-1]:
        parse = spline[-1].split('/')
        print(parse[-3],parse[-2],parse[-1])
        print(line)
        streams['streams'][parse[-3]] = {parse[-2]:parse[-1][:-1],'lastSeen':int(time.time())}
    time.sleep(.2)
    
    with open('index.html', 'w') as f:
        js = json.dump(streams, f)




