#!/usr/bin/env python
import sys
import cv2
import numpy as np
import os

# Distance from tape is 15 to 20 inches

# Restore defaults for cam
os.system('v4l2-ctl -c exposure=12q0')
os.system('v4l2-ctl -c contrast=32')

#Creating Windows
cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
cv2.resizeWindow("frame", 100,100)
cv2.namedWindow("original", cv2.WINDOW_NORMAL)
cv2.resizeWindow("original", 100,100)
cv2.namedWindow('image', cv2.WINDOW_NORMAL)

#Strings
hh = 'hue high'
sh = 'saturation high'
vh = 'value high'

hl = 'hue low'
sl = 'saturation low'
vl = 'value low'
                      
#Creating Trackbars with defaults
#Lower
cv2.createTrackbar(hl, 'image', 0, 179, lambda:none)	
cv2.createTrackbar(sl, 'image', 0, 255, lambda:none)	
cv2.createTrackbar(vl, 'image', 235, 255, lambda:none)	
#Upper
cv2.createTrackbar(hh, 'image', 14, 179, lambda:none)	
cv2.createTrackbar(sh, 'image', 23, 255, lambda:none)	
cv2.createTrackbar(vh, 'image', 255, 255, lambda:none)	

#Erosion
erosionKernel = np.ones((3,3), np.uint8)
dilateKernel = np.ones((0,0), np.uint8)

cap = cv2.VideoCapture(0)

#Loop
while(True):
        
	# Reads every frame

	ret, img = cap.read()
	default = img
	height, width = img.shape[:2]
	
	# 'q' breaks operation
	if cv2.waitKey(1) & 0xFF == ord('q'):
        	break
	
	# Converts image to hsv
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
	# Reads Trackbar Position
	ahl=cv2.getTrackbarPos(hl, 'image')
	asl=cv2.getTrackbarPos(sl, 'image')
	avl=cv2.getTrackbarPos(vl, 'image')
	ahh=cv2.getTrackbarPos(hh, 'image')
	ash=cv2.getTrackbarPos(sh, 'image')
	avh=cv2.getTrackbarPos(vh, 'image')

	# Make array
	hsvl = np.array([ahl,asl,avl])
	hsvh = np.array([ahh,ash,avh])

	# Apply range on a mask
	mask = cv2.inRange(hsv, hsvl, hsvh)
	res = cv2.bitwise_and(img, img, mask=mask)

	# Create a new image that contains yellow where the color was detected
	img = cv2.inRange(hsv, hsvl, hsvh)
	img = cv2.erode(img, erosionKernel, iterations =1)
	img = cv2.dilate(img, dilateKernel, iterations=1)

	# Blur to get rid of sawtooth effect
	img= cv2.blur(img, (3,3))
	    
	# Contours
	#Finding contours
	
	#cnts = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	"""if len(cnts) > 0:
		for cnt in cnts:
			# Sorts from largest to smallest
			# cntsSorted = sorted(cnts, key = lambda x: cv2.contourArea(x))
			# cv2.contourArea(cnt)
			# Draw the contour over image
			area = cv2.contourArea(cnts)
		
		# Draw a minimum area rectangle around the contour
			rect1 = np.int32(cv2.boxPoints(cv2.minAreaRect(cnts)))
		
		# Draw the contour over image
			cv2.drawContours(img, [rect1], -1, (255, 0, 0), 2)"""

	

	cv2.imshow('original', default)
	cv2.imshow('image', res)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
