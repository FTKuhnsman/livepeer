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

#%%
    
if __name__ == "__main__":
    r = requests.post('http://{}:{}/'.format(ts[2],ts[3]), json={'command':'unregister','ipAddr':ts[1]})
