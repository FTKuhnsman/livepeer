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
count = int(sys.argv[3])

while True:
    print('https://{}/stream/{}/480p/{}.ts'.format(str(sys.argv[1]),str(sys.argv[2]),str(count)))

    cap = cv2.VideoCapture('https://{}/stream/{}/480p/{}.ts'.format(str(sys.argv[1]),str(sys.argv[2]),str(count)))
    
    # Check if camera opened successfully
    if (cap.isOpened()== False): 
      print("Error opening video stream or file")
      continue
    
    # Read until video is completed
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
    
        # Display the resulting frame
            cv2.imshow('Frame',frame)
    
        # Press Q on keyboard to  exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            break
    count += 1
    print(count)
cap.release()
# When everything done, release the video capture object


# Closes all the frames
cv2.destroyAllWindows()