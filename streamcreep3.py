#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 21:20:02 2022

@author: ghost
"""

import cv2

import sys

print(sys.argv)


# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
count = int(sys.argv[4])

while True:
    proc1 = sub.Popen(('sudo','tail','-f','/var/log/livepeer/livepeer.log'), stdout=sub.PIPE)
    while go:
        byte = proc1.stdout.readline()
        line = byte.decode('utf-8')
        spline = line.split(' ')
        if '.ts' in spline[-1]:
            parse = spline[-1].split('/')
            print(parse[-3],parse[-2],parse[-1])
            streams[parse[-3]] = {parse[-2]:parse[-1]}
            '''
            s = list(streams.keys())[0]
            res = list(streams[s])['res']
            '''
cap.release()
# When everything done, release the video capture object


# Closes all the frames
cv2.destroyAllWindows()