# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import subprocess as sub
import json
import requests

url = 'http://ipinfo.io/8.8.8.8'
#response = requests.get(url)

ignore = ['192.168.0.28','47.205.87.4','127.0.0.1','45.76.61.64']
ip_list = []
ip_check = []

tcpdump = sub.Popen(('sudo', 'tcpdump', '-ni','any','port','8935'), stdout=sub.PIPE)
while True:
    byte = tcpdump.stdout.readline()
    line = byte.decode('utf-8')
    spline = line.split(' ')
    size = int(str(spline[-1]).replace('/n',''))
    if not any(s in spline[2] for s in ignore):
        #print(line)
        #print(size)
        if not size == 0:
            spip = spline[2].split('.')
            ip = '.'.join(spip[0:4])
            if not ip in ip_check:
                
                
                
                url = 'http://ipinfo.io/{}'.format(ip)
                response = requests.get(url)
                rjs = response.json()
                ip_check.append(ip)
                ip_list.append({'IP':ip, 'City':rjs['city'],'Region':rjs['region'],'Country':rjs['country'], 'Org':rjs['org']})
                
                print(ip_list[-1])