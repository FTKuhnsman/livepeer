# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 17:14:43 2021

@author: jkuhnsman
"""

import os

print(os.getcwd())

orch1 = '45.32.168.255'

drop_orch = 'iptables -t nat -D PREROUTING -i enp1s0 -p tcp --dport 8935 -j DNAT --to {}'
add_orch = 'iptables -t nat -A PREROUTING -i enp1s0 -p tcp --dport 8935 -j DNAT --to {}'

#add orch1
os.system(add_orch.format(orch1))

#drop orch1
os.system(drop_orch.format(orch1))
