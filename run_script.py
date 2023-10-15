from ppadb.client import Client
import cv2
import numpy as np
from PIL import ImageGrab
import mss
import imutils
import math
import Line_segment_intersect as lsi
import Click_at_mouse_position as camp
import time

## Time delay after each shoot
t = 1.5

## Shooting adjustmentdue to delay
height_add = 260
width_add = 200

shoot_flag = 0

sct = mss.mss()

monitor = sct.monitors[1]

# Capture a bbox using percent values
left = monitor["left"] + monitor["width"] * 2 // 100  # 5% from the left
top = monitor["top"] + monitor["height"] * 15 // 100  # 5% from the top
right = left + 350  # 400px width
lower = top + 700  # 400px height
bbox = (left, top, right, lower)


Width = 350
Height = 700
scale = 0.00392

# read class names from text file
classes = None
with open('classes.txt', 'r') as f:
	classes = [line.strip() for line in f.readlines()]

# generate different colors for different classes 
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

# read pre-trained model and config file
net = cv2.dnn.readNet('yolov4-obj_last.weights','yolov4-obj.cfg')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

# function to draw bounding box on the detected object with class name
def draw_bounding_box(img, class_id, confidence, x, y, x_plus_w, y_plus_h):

	label = str(classes[class_id])

	color = COLORS[class_id]

	cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)

	cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


# function to get the output layer names 
# in the architecture
def get_output_layers(net):
    
	layer_names = net.getLayerNames()
    
	output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

	return output_layers

# function to get the contours
def get_the_contours(img_arr, l_b, u_b):
	hsv = cv2.cvtColor(img_arr, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, l_b, u_b)

	blurred = cv2.GaussianBlur(mask, (5, 5), 0)
	thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

	# find contours in the thresholded image
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

	return cnts



while True:
	img = sct.grab(bbox)
	img_arr = np.array(img)
	img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
	img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)

	# contours for nozzle
	l_b_nozz = np.array([0, 0, 50])
	u_b_nozz = np.array([255, 10, 100])

	cnts_nozz = get_the_contours(img_arr, l_b_nozz, u_b_nozz)

	# contours for butt
	l_b_butt = np.array([0, 26, 30])
	u_b_butt = np.array([28, 255, 134])

	cnts_butt = get_the_contours(img_arr, l_b_butt, u_b_butt)

	# get the contours for nozzle with maximum area
	cnt_nozz_max = []
	for cnt in cnts_nozz:
		if len(cnt_nozz_max) == 0:
			cnt_nozz_max = cnt
		elif cv2.contourArea(cnt) > cv2.contourArea(cnt_nozz_max):
			cnt_nozz_max = cnt


	# get the contours for butt with maximum area
	cnt_butt_max = []
	for cnt in cnts_butt:
		if len(cnt_butt_max) == 0:
			cnt_butt_max = cnt
		elif cv2.contourArea(cnt) > cv2.contourArea(cnt_butt_max):
			cnt_butt_max = cnt

	# create a line for nozzle across the entire screen
	rows,cols = img_arr.shape[:2]
	try:
		[vx,vy,x,y] = cv2.fitLine(cnt_nozz_max, cv2.DIST_L2,0,0.01,0.01)
		lefty_nozz = int((-x*vy/vx) + y)
		righty_nozz = int(((cols-x)*vy/vx)+y)
		cv2.line(img_arr,(cols-1,righty_nozz),(0,lefty_nozz),(0,255,0),2)
	except:
		continue

	# create a line for butt across the entire screen
	try:
		[vx,vy,x,y] = cv2.fitLine(cnt_butt_max, cv2.DIST_L2,0,0.01,0.01)
		lefty_butt = int((-x*vy/vx) + y)
		righty_butt = int(((cols-x)*vy/vx)+y)
		cv2.line(img_arr,(cols-1,righty_butt),(0,lefty_butt),(255,0,0),2)
	except:
		continue

	# Get the centroid position for the maximum area contour of the nozzle
	try:
		M = cv2.moments(cnt_nozz_max)
		cX = int(M['m10']/M['m00'])
		cY = int(M['m01']/M['m00'])
		cv2.circle(img_arr, (cX, cY), 4, (0, 0, 255), -1)

		# Intersection Point for the nozzle and butt line
		eq_a = cols -1
		eq_b = righty_nozz
		eq_c = lefty_nozz
		eq_d = righty_butt
		eq_e = lefty_butt

		int_X = int((eq_c - eq_e)/(((eq_c - eq_b)/eq_a) - ((eq_e - eq_d)/eq_a)))
		int_Y = int(eq_c-(((eq_c - eq_b)/eq_a)*int_X))

		cv2.circle(img_arr, (int_X, int_Y), 4, (0, 0, 255), -1)
		
		# Draw a line crossing the two points
		cv2.line(img_arr, (int_X, int_Y), (cX, cY), (0,0,255),2)
	except:
		continue

	
	# create input blob 
	blob = cv2.dnn.blobFromImage(img_arr, scale, (416,416), (0,0,0), True, crop=False)

	# # set input blob for the network
	net.setInput(blob)

	# # run inference through the network
	# # and gather predictions from output layers
	outs = net.forward(get_output_layers(net))

	# initialization
	class_ids = []
	confidences = []
	boxes = []
	conf_threshold = 0.5
	nms_threshold = 0.4

	# for each detecion from each output layer 
	# get the confidence, class id, bounding box params
	# and ignore weak detections (confidence < 0.5)
	for out in outs:
		for detection in out:
			scores = detection[5:]
			class_id = np.argmax(scores)
			confidence = scores[class_id]
			if confidence > 0.98 and class_id != 2:
				center_x = int(detection[0] * Width)
				center_y = int(detection[1] * Height)
				w = int(detection[2] * Width)
				h = int(detection[3] * Height)
				x = center_x - w / 2
				y = center_y - h / 2
				class_ids.append(class_id)
				confidences.append(float(confidence))
				boxes.append([x, y, w, h, center_x, center_y])

	# apply non-max suppression
	indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)


	# go through the detections remaining
	# after nms and draw bounding box
	for i in indices:
		i = i[0]
		box = boxes[i]
		x = box[0]
		y = box[1]
		w = box[2]
		h = box[3]
		cx = box[4]
		cy = box[5]

		draw_bounding_box(img_arr, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))
	    
		if str(classes[class_ids[i]]) == 'hit':
			p1 = lsi.Point(int_X, int_Y)
			q1 = lsi.Point(cX, cY)
			if w > h:
				if round(cy) > 400:
					cv2.line(img_arr, (round(cx-width_add), round(cy)), (round(cx-w/10), round(cy)), (0,0,255), 2)
					p2 = lsi.Point(round(cx-width_add), round(cy))
					q2 = lsi.Point(round(cx-w/10), round(cy))
					# print('p1=(',p1.x,',',p1.y,'), p2=(',p2.x,',',p2.y,'), q1=(',q1.x,',',q1.y,'), q2=(',q2.x,',',q2.y,')')
					if lsi.perp_dist(p2,q2,q1) < lsi.perp_dist(p2,q2,p1):
						intersect_pt = lsi.get_intersect_pts(p1,q1,p2,q2)
						if round(lsi.plain_dist(intersect_pt,p2) + lsi.plain_dist(intersect_pt,q2)) == round(lsi.plain_dist(p2,q2)):
							# print('HIT.......!!!!')
							camp.click_at_pos(78,436)
							time.sleep(t)
				else:
					cv2.line(img_arr, (round(cx+w/10), round(cy)), (round(cx+width_add), round(cy)), (0,0,255), 2)
					p2 = lsi.Point(round(cx+w/10), round(cy))
					q2 = lsi.Point(round(cx+width_add), round(cy))
					# print('p1=(',p1.x,',',p1.y,'), p2=(',p2.x,',',p2.y,'), q1=(',q1.x,',',q1.y,'), q2=(',q2.x,',',q2.y,')')
					if lsi.perp_dist(p2,q2,q1) < lsi.perp_dist(p2,q2,p1):
						intersect_pt = lsi.get_intersect_pts(p1,q1,p2,q2)
						if round(lsi.plain_dist(intersect_pt,p2) + lsi.plain_dist(intersect_pt,q2)) == round(lsi.plain_dist(p2,q2)):
							# print('HIT.......!!!!')
							camp.click_at_pos(78,436)
							time.sleep(t)
			else:
				if round(cx) > 200:
					cv2.line(img_arr, (round(cx), round(cy-h/10)), (round(cx), round(cy+height_add)), (0,0,255), 2)
					p2 = lsi.Point(round(cx), round(cy-h/10))
					q2 = lsi.Point(round(cx), round(cy+height_add))
					# print('p1=(',p1.x,',',p1.y,'), p2=(',p2.x,',',p2.y,'), q1=(',q1.x,',',q1.y,'), q2=(',q2.x,',',q2.y,')')
					if lsi.perp_dist(p2,q2,q1) < lsi.perp_dist(p2,q2,p1):
						intersect_pt = lsi.get_intersect_pts(p1,q1,p2,q2)
						if round(lsi.plain_dist(intersect_pt,p2) + lsi.plain_dist(intersect_pt,q2)) == round(lsi.plain_dist(p2,q2)):
							# print('HIT.......!!!!')
							camp.click_at_pos(78,436)
							time.sleep(t)
				else:
					cv2.line(img_arr, (round(cx), round(cy-height_add)), (round(cx), round(cy+h/10)), (0,0,255), 2)
					p2 = lsi.Point(round(cx), round(cy-height_add))
					q2 = lsi.Point(round(cx), round(cy+h/10))
					# print('p1=(',p1.x,',',p1.y,'), p2=(',p2.x,',',p2.y,'), q1=(',q1.x,',',q1.y,'), q2=(',q2.x,',',q2.y,')')
					if lsi.perp_dist(p2,q2,q1) < lsi.perp_dist(p2,q2,p1):
						intersect_pt = lsi.get_intersect_pts(p1,q1,p2,q2)
						if round(lsi.plain_dist(intersect_pt,p2) + lsi.plain_dist(intersect_pt,q2)) == round(lsi.plain_dist(p2,q2)):
							# print('HIT.......!!!!')
							camp.click_at_pos(78,436)
							time.sleep(t)

	cv2.imshow('frame', img_arr)

	if cv2.waitKey(25) & 0xFF == ord('q'):
		cv2.destroyAllWindows()
		running = False
		break