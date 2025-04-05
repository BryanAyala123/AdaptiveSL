#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  5 11:34:33 2025

@author: bryanayala
"""


import cv2
import imutils

# Access the default camera
cap = cv2.VideoCapture(0)

FirstFrame = None
# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

while(True):
    # Read a frame from the camera
    ret, frame = cap.read()
    

    # Check if the frame was read successfully
    if not ret:
        print("Error: Could not read frame")
        break

    ret = imutils.resize(ret, width = 500)
    gray = cv2.cvtColor(ret, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21,21), 0)

    # Display the frame
    cv2.imshow('Camera Feed', frame)

    if FirstFrame is None:
        FirstFrame = gray
        continue

    frameDelta = cv2.absdiff(FirstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close windows
cap.release()
cv2.destroyAllWindows()