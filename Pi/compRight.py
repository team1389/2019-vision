from __future__ import print_function
import argparse
import warnings
import sys
sys.path.append('/usr/local/lib/python3.5/dist-packages')
import cv2 as cv
import numpy as np
import imutils
import os
from imutils import perspective
from networktables import NetworkTables

#Initializing NetworkTables
NetworkTables.initialize(server='10.13.89.2')
table = NetworkTables.getTable('vision')

#Setting up argument parser
parser = argparse.ArgumentParser()
parser.add_argument("--camera", help = 'camera device number', default = 0, type = int)
args = parser.parse_args()

#Setting up camera
cap = cv.VideoCapture(args.camera)

#Setting HSV values
lower = np.array([0, 0, 254])
upper = np.array([9, 13, 255])

#Erosion
erosionKernel = np.ones((3,3), np.uint8)
dilateKernel = np.ones((0,0), np.uint8)

window_width = 640
window_height = 480

bounding_area_min = 2600
#Sorts contours from left to right
def threshold(frame, lower, upper):
	frame_HSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
	frame_threshold = cv.inRange(frame_HSV, lower, upper)
	frame_threshold = cv.erode(frame_threshold, erosionKernel, iterations =1)
	frame_threshold = cv.dilate(frame_threshold, dilateKernel, iterations=1)
	
	
	return (frame_threshold)

def sort_contours(cnts):

	boundingBoxes = [cv.boundingRect(c) for c in cnts]
	(cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes), key = lambda b:b[1][0], reverse=True))

	return (cnts, boundingBoxes)
	
def draw_bounding_boxes(cnt):
	ctr = np.array(box).reshape((-1,1,2)).astype(np.int32)
	cv.drawContours(frame, [ctr], -1, (255, 0, 0), 2)

def get_centers(cnt, frame, centers):
	M = cv.moments(cnt)
	cx = int(M['m10']/M['m00'])
	cy = int(M['m01']/M['m00'])
	cv.circle(frame, (cx, cy), 10, (0, 0, 255), -1)
	centers.append(cx)

def get_centers_bisect(cnt1, cnt2):
	bisect = ((cnt1 + cnt2) / 2)
	cv.circle(frame, (int(bisect), int(window_height/2)), 10, (0, 255, 255), -1)
	table.putNumber("RightSideX", bisect)
	
def sort_side(angle, contourIndex):
	if (angle>= -45):
		right.append(contourIndex)
	else:
		left.append(contourIndex)
			
def match_sides(c, left, right):
	if len(right) > 0 and len(left) == 1:
		if(right[0] == 0 and left[0] == 1):
			get_centers_bisect(centers[0], centers[1])
	elif len(right) == 1 and len(left) == 2:
		if right[0] == 1 and left[1] == 2:
			get_centers_bisect(centers[1], centers[2])
	else:
		table.putNumber("RightSideX", 320)

while True:

	#No networktables case for when there are contours, but the contours are smaller than min
	if table.getString("State", "right") == "left":
		os.system('python compLeft.py &')
		sys.exit()
		

	ret, frame = cap.read()
	if frame is None:
		break;

	contours = cv.findContours(threshold(frame, lower, upper).copy(), 
	cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
	contours = imutils.grab_contours(contours)

	centers = []
	left = []
	right = []
	cnts = []

	if len(contours) == 0:
		table.putNumber("RightSideX", 320)

	if len(contours) > 0:
		for c in contours:
			area = cv.contourArea(c)
			if area > bounding_area_min:
				cnts.append(c)
	if len(cnts) > 0:

		(cnts, boundingBoxes) = sort_contours(cnts)	

		for contourIndex in range(0, len(cnts)):

			c = cnts[contourIndex]
		
			rect = cv.minAreaRect(c)
			box = cv.boxPoints(rect)		

			draw_bounding_boxes(c)
			get_centers(c, frame, centers)
			
			angle = rect[2]
			sort_side(angle, contourIndex)
			
			match_sides(c, left, right)
					
					
	key = cv.waitKey(1) & 0xFF
	if key == ord('q'):
		break
