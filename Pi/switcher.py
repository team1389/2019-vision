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

i = 0

if table.getBoolean("SwitchSides", False) && (i % 0 == 0):
		os.system('python right.py')
		print("switchsides triggered")
		os._exit()
