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

def draw_lines(cnt, frame, cols, lefty, righty):

	cv.line(frame, (cols - 1, righty), (0, lefty), (0, 255, 0), 2)


	#Saving the line being drawn 			
	if lines == None:
		lines.append(cols - 1)
		lines.append(righty)
		lines.append(0)
		lines.append(lefty)
		print("Length of lines array", len(lines))
	else:
		lines.append(cols - 1)
		lines.append(righty)
		lines.append(0)
		lines.append(lefty)

	return (lines)
	
def calculate_first_intersection(xCoord, yCoord, lines, window_height):
	u = ((lines[6] - lines[4]) * (lines[1]-lines[5]) - (lines[7] - lines[5])*(lines[0] - lines[4]))/((lines[7] - lines[5])*(lines[2] - lines[0]) - (lines[6] - lines[4])*(lines[3]-lines[1]))

	y = righty + u * (lefty - righty)
	yCoord = int(y)
	#if yCoord < lines[0]:
	if yCoord < window_height:			
		x = (cols-1) + u * (0 - (cols - 1))
		xCoord = int(x)
		cv.circle(frame, (xCoord,yCoord), 7, (0,0,255), -1)
		cv.circle(frame, (xCoord,240), 7, (255,0,255), -1)
	else:
		print("excluding because of height")
		
def calculate_second_intersection(xCoordTwo, yCoordTwo, lines, window_height):
	uRight = ((lines[10] - lines[8]) * (lines[5]-lines[9]) - (lines[11] - lines[9])*(lines[4] - lines[8]))/((lines[11] - lines[9])*(lines[6] - lines[4]) - (lines[10] - lines[8])*(lines[7]-lines[5]))

	yTwo = righty + uRight * (lefty - righty)
	yCoordTwo = int(yTwo)
	if yCoordTwo < window_height:
		xTwo = (cols-1) + uRight * (0 - (cols - 1))
		xCoordTwo = int(xTwo)
		cv.circle(frame, (xCoordTwo,yCoordTwo), 7, (0,0,255), -1)
		cv.circle(frame, (xCoordTwo,240), 7, (255,0,255), -1)
	else:
		print("excluding because of height")


while True:

	ret, frame = cap.read()
	if frame is None:
		break;

	cnts = cv.findContours(threshold(frame, lower, upper).copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

	lines = []

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
			
				rows,cols = frame.shape[:2]
				[vx,vy,x,y] = cv.fitLine(c, cv.DIST_L2, 0, 0.01, 0.01)
				lefty = int((-x * vy/vx) + y)
				righty = int(((cols - x) * vy/vx) + y)

				draw_lines(c, frame, cols, lefty, righty)


		#setting defaults		
		yCoord = window_height
		yCoordTwo = window_height
		xCoord = window_width/2 
		xCoordTwo = window_width/2

		#Finds the intersection between midlines of contours
		
		if len(lines) > 7:
			calculate_first_intersection(xCoord, yCoord, lines, window_height)


		#look at calculations for u for this one, causes point to be displayed on other line
		if len(lines) > 11:
			calculate_second_intersection(xCoordTwo, yCoordTwo, lines, window_height)
			
		#calculations for coord for lines array has 0,0 start from bottom left, ycoord starts from top left, weird lol
		if yCoordTwo < yCoord:
			table.putNumber("X", xCoordTwo)
	
		else:
			cv.circle(frame, (0,0), 7, (0,0,255), -1)
	#Making windows
	cv.imshow(window_capture_name, frame)
	cv.imshow(window_detection_name, threshold(frame, lower, upper))

	key = cv.waitKey(1) & 0xFF
	if key == ord('q'):
		break
