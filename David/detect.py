# TODO:

import cv2
import numpy as np
print(cv2.__version__)


class ShapeDetector:
  def __init__(self):
    pass

  def hello(self):
    return "hello"

  def detect(self, c):
    # initialize the shape name and approximate the contour
    shape = "unidentified"
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.04 * peri, True)

    # if the shape is a triangle, it will have 3 vertices
    if len(approx) == 3:
      shape = "triangle"

    # if the shape has 4 vertices, it is either a square or a rectangle
    elif len(approx) == 4:
      # compute the bounding box of the contour and use the
      # bounding box to compute the aspect ratio

      (x, y, w, h) = cv2.boundingRect(approx)
      ar = w / float(h)

      # a square will have an aspect ratio that is approximately
      # equal to one, otherwise, the shape is a rectangle
      shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"

      # otherwise, we assume the shape is a circle
    else:
      shape = "circle"

    # return the name of the shape
    return shape

lower_green = np.array([75, 200, 200])
upper_green = np.array([85, 255, 255])
cv2.namedWindow('win1', cv2.WINDOW_NORMAL)
cv2.resizeWindow('win1', 250, 250)
cv2.moveWindow('win1', 0, 0)
cv2.namedWindow('win2', cv2.WINDOW_NORMAL)
cv2.resizeWindow('win2', 250, 250)
cv2.moveWindow('win2', 0, 275)
cv2.namedWindow('win3', cv2.WINDOW_NORMAL)
cv2.resizeWindow('win3', 250, 250)
cv2.moveWindow('win3', 0, 550)

f = "./rectangles_dirty.jpg"
image = cv2.imread(f)

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, lower_green, upper_green)
cv2.imshow('win1', mask)

# Bitwise-AND mask and original image
res = cv2.bitwise_and(image, image, mask=mask)

cv2.imshow('win2', res)

kernel = np.ones((3, 3), np.uint8)
opened = cv2.morphologyEx(res, cv2.MORPH_OPEN, kernel)
blur = cv2.blur(opened, (3, 3))

# ret, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV)
tmp = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)  # findcontours requires a GRAY image
cnts = cv2.findContours(tmp.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

MIN_AREA = 5000
sd = ShapeDetector()
if len(cnts) != 0:
  # TODO: cycle through all the contours, and ignore any that have an area less than a size threshold
  for cnt in cnts:
    area = cv2.contourArea(cnt)
    if area > MIN_AREA:
      print(area)
      cv2.drawContours(blur, cnt, -1, (0, 0, 255), 5)
      M = cv2.moments(cnt)
      cx = int(M['m10'] / M['m00'])
      cy = int(M['m01'] / M['m00'])
      print(cx)
      print(cy)
      print(sd.detect(cnt))
      cv2.circle(blur, (cx, cy), 10, (0, 0, 255), -1)

cv2.imshow('win3', blur)

wait = True
while wait:
    wait = cv2.waitKey() == 'q113'
