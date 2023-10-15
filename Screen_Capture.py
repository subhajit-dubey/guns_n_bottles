from ppadb.client import Client
import cv2
import numpy as np
from PIL import ImageGrab
import mss

sct = mss.mss()

monitor = sct.monitors[1]

# Capture a bbox using percent values
left = monitor["left"] + monitor["width"] * 2 // 100  # 5% from the left
top = monitor["top"] + monitor["height"] * 15 // 100  # 5% from the top
right = left + 350  # 400px width
lower = top + 700  # 400px height
bbox = (left, top, right, lower)

i = 1
while True:
	img = sct.grab(bbox)
	img_arr = np.array(img)
	img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
	img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)

	cv2.imshow('frame', img_arr)
	cv2.imwrite('Screenshot_' + str(i) + '.jpg', img_arr)
	i = i + 1

	if cv2.waitKey(25) & 0xFF == ord('q'):
		cv2.destroyAllWindows()
		running = False
		break