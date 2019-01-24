from __future__ import print_function
import argparse
import warnings
import sys
sys.path.append('/usr/local/lib/python3.5/dist-packages')
import cv2 as cv
import numpy as np
import imutils

window_capture_name = 'Video Capture'
window_detection_name = 'Object Detection'

#Setting up argument parser
parser = argparse.ArgumentParser()
parser.add_argument("--camera", help = 'camera device number', default = 0, type = int)
args = parser.parse_args()

#Setting up camera
cap = cv.VideoCapture(args.camera)

#Setting HSV values
lower = np.array([0, 0, 255])
upper = np.array([90, 95, 255])

#Erosion
erosionKernel = np.ones((3,3), np.uint8)
dilateKernel = np.ones((0,0), np.uint8)

#Setting up windows
cv.namedWindow(window_capture_name)
cv.namedWindow(window_detection_name)

while True:

	ret, frame = cap.read()
	if frame is None:
		break;
	
	#Thresholding
	frame_HSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
	frame_threshold = cv.inRange(frame_HSV, lower, upper)
	frame_threshold = cv.erode(frame_threshold, erosionKernel, iterations =1)
	frame_threshold = cv.dilate(frame_threshold, dilateKernel, iterations=1)
	bounding_area_min = 2000

	#Finding contours
	cnts = cv.findContours(frame_threshold.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)


	for c in cnts:
		#if contour is too small, ignore
		area = cv.contourArea(c)
		
		if area > bounding_area_min:		
			#Draw bounding boxes
			rect = cv.minAreaRect(c)
			box = cv.boxPoints(rect)		
			ctr = np.array(box).reshape((-1,1,2)).astype(np.int32)
			cv.drawContours(frame, [ctr], -1, (255, 0, 0), 2)
			
			#compute center of contours
			M = cv.moments(c)
			cX = int(M['m10'] / M['m00'])
			cY = int(M['m01'] / M['m00'])

			#draw center of contours
			cv.circle(frame, (cX, cY), 7, (255, 0, 0), -1)

			
			

	#Making windows
	cv.imshow(window_capture_name, frame)
	cv.imshow(window_detection_name, frame_threshold)

	key = cv.waitKey(1) & 0xFF
	if key == ord('q'):
		break
