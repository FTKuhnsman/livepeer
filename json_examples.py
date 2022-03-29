# -*- coding: utf-8 -*-
"""
Created on Tue Oct 26 16:44:13 2021

@author: jkuhnsman
"""

json = {'command':'register_orchestrator',
        'type':'physical',
        'ipAddr':'0.0.0.0',
        'maxSessions':'10'}

json = {'command':'register_orchestrator',
        'type':'virtual',
        'ipAddr':'0.0.0.0',
        'maxSessions':'10',
        't_id':'i-014c83a7f386f9e6b'}

js = {'command':'update_metrics',
        'ipAddr':'0.0.0.0',
        'metrics':{'maxSessions':10, 'currentSessions':5}
        }
