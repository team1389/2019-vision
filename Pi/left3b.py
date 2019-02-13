from __future__ import print_function
import argparse
import warnings
import sys
sys.path.append('/usr/local/lib/python3.5/dist-packages')
import cv2 as cv
import numpy as np
import imutils
from imutils import perspective
from networktables import NetworkTables

#Initializing NetworkTables
NetworkTables.initialize(server='10.13.89.2')
table = NetworkTables.getTable('vision')

#Setting up argument parser
parser = argparse.ArgumentParser()
parser.add_argument("--camera", help = 'camera device number', default =
 0, type = int)
args = parser.parse_args()

#Setting up camera
cap = cv.VideoCapture(args.camera)

#Setting HSV values
lower = np.array([0, 0, 254])
upper = np.array([9, 13, 255])

#Erosion
erosionKernel = np.ones((3,3), np.uint8)
dilateKernel = np.ones((0,0), np.uint8)

#Setting up windows
window_capture_name = 'Video Capture'
window_detection_name = 'Object Detection'
cv.namedWindow(window_capture_name)
cv.namedWindow(window_detection_name)

window_width = 640
window_height = 480

bounding_area_min = 3000
#Sorts contours from left to right
def threshold(frame, lower, upper):
	frame_HSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
	frame_threshold = cv.inRange(frame_HSV, lower, upper)
	frame_threshold = cv.erode(frame_threshold, erosionKernel, iterations =1)
	frame_threshold = cv.dilate(frame_threshold, dilateKernel, iterations=1)
	
	
	return (frame_threshold)

def sort_contours(cnts):

	boundingBoxes = [cv.boundingRect(c) for c in cnts]
	(cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes), key = lambda b:b[1][0], reverse=False))

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

def get_centers_bisect(centers):
	bisect = (centers[0] + centers[1] / 2)
	cv.circle(frame, (bisect, int(window_height/2)), 10, (0, 255, 255), -1)
	return bisect
	
while True:

	ret, frame = cap.read()
	if frame is None:
		break;

	cnts = cv.findContours(threshold(frame, lower, upper).copy(), 
	cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

	centers = []

	if len(cnts) == 0:
		table.putNumber("X", 320)
		print("nothing detected")

	if len(cnts) > 0:

		(cnts, boundingBoxes) = sort_contours(cnts)	

		for c in cnts:

			area = cv.contourArea(c)
		
			if area > bounding_area_min:

				rect = cv.minAreaRect(c)
				box = cv.boxPoints(rect)		

				draw_bounding_boxes(c)
				get_centers(c, frame, centers)
			


		#setting defaults		
		yCoord = window_height
		yCoordTwo = window_height
		xCoord = window_width/2 
		xCoordTwo = window_width/2



			
		#calculations for coord for lines array has 0,0 start from 
		#bottom left, ycoord starts from top left, weird lol
		#table.putNumber("X", xCoordTwo)
		print(xCoord)
	
					
	#Making windows
	cv.imshow(window_capture_name, frame)
	cv.imshow(window_detection_name, threshold(frame, lower, upper))

	key = cv.waitKey(1) & 0xFF
	if key == ord('q'):
		break
