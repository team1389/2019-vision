from __future__ import print_function
import argparse
import warnings
import sys
sys.path.append('/usr/local/lib/python3.5/dist-packages')
import cv2 as cv
import numpy as np
import imutils
from imutils import perspective

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
upper = np.array([90, 180, 255])

#Erosion
erosionKernel = np.ones((3,3), np.uint8)
dilateKernel = np.ones((0,0), np.uint8)

#Setting up windows
cv.namedWindow(window_capture_name)
cv.namedWindow(window_detection_name)

def sort_contours(cnts):

	boundingBoxes = [cv.boundingRect(c) for c in cnts]
	(cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes), key = lambda b:b[1][0], reverse=False))

	return (cnts, boundingBoxes)
	
while True:

	ret, frame = cap.read()
	if frame is None:
		break;
	
	#Thresholding
	frame_HSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
	frame_threshold = cv.inRange(frame_HSV, lower, upper)
	frame_threshold = cv.erode(frame_threshold, erosionKernel, iterations =1)
	frame_threshold = cv.dilate(frame_threshold, dilateKernel, iterations=1)
	bounding_area_min = 1500

	#Finding contours
	cnts = cv.findContours(frame_threshold.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

	lines = []
	(cnts, boundingBoxes) = sort_contours(cnts)	
	for c in cnts:
		#if contour is too small, ignore
		area = cv.contourArea(c)
		
		if area > bounding_area_min:		
			#Draw bounding boxes
			rect = cv.minAreaRect(c)
			box = cv.boxPoints(rect)
			ctr = np.array(box).reshape((-1,1,2)).astype(np.int32)
			#vertices = perspective.order_points(ctr)
			
			cv.drawContours(frame, [ctr], -1, (255, 0, 0), 2)
			
			#Drawing lines through the center of contours
			rows,cols = frame.shape[:2]
			[vx,vy,x,y] = cv.fitLine(c, cv.DIST_L2, 0, 0.01, 0.01)
			lefty = int((-x * vy/vx) + y)
			righty = int(((cols - x) * vy/vx) + y)
			cv.line(frame, (cols - 1, righty), (0, lefty), (0, 255, 0), 2)
			ctr = np.array(box).reshape((-1,1,2)).astype(np.int32)
 

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
			

	yCoord = 0
	yCoordTwo = 0
	xCoord = 0 
	xCoordTwo = 0
	#Finds the intersection between midlines of contours
	if len(lines) > 7:
		u = ((lines[6] - lines[4]) * (lines[1]-lines[5]) - (lines[7] - lines[5])*(lines[0] - lines[4]))/((lines[7] - lines[5])*(lines[2] - lines[0]) - (lines[6] - lines[4])*(lines[3]-lines[1]))
		x = (cols-1) + u * (0 - (cols - 1))
		xCoord = int(x)
		y = righty + u * (lefty - righty)
		yCoord = int(y)
		cv.circle(frame, (xCoord,yCoord), 7, (0,0,255), -1)
	if len(lines) > 12:
		u = ((lines[13] - lines[11]) * (lines[8]-lines[12]) - (lines[14] - lines[12])*(lines[7] - lines[11]))/((lines[14] - lines[12])*(lines[9] - lines[7]) - (lines[13] - lines[11])*(lines[10]-lines[8]))
		xTwo = (cols-1) + u * (0 - (cols - 1))
		xCoordTwo = int(x)
		yTwo = righty + u * (lefty - righty)
		yCoordTwo = int(y)
		cv.circle(frame, (xCoordTwo, yCoordTwo), 7, (0,0,255), -1)
	if yCoord > yCoordTwo:
		print(xCoord)
	else:
		print(xCoordTwo)
		
	#Making windows
	cv.imshow(window_capture_name, frame)
	cv.imshow(window_detection_name, frame_threshold)

	key = cv.waitKey(1) & 0xFF
	if key == ord('q'):
		break
