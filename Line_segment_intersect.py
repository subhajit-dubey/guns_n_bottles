# A Python3 program to find if 2 given line segments intersect or not 
import math

class Point: 
	def __init__(self, x, y): 
		self.x = x 
		self.y = y 

# Given three colinear points p, q, r, the function checks if 
# point q lies on line segment 'pr' 
def onSegment(p, q, r): 
	if ( (q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
		(q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))): 
		return True
	return False

def orientation(p, q, r): 
	# to find the orientation of an ordered triplet (p,q,r) 
	# function returns the following values: 
	# 0 : Colinear points 
	# 1 : Clockwise points 
	# 2 : Counterclockwise 
	
	# See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/ 
	# for details of below formula. 
	
	val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y)) 
	if (val > 0): 
		
		# Clockwise orientation 
		return 1
	elif (val < 0): 
		
		# Counterclockwise orientation 
		return 2
	else: 
		
		# Colinear orientation 
		return 0

# The main function that returns true if 
# the line segment 'p1q1' and 'p2q2' intersect. 
def doIntersect(p1,q1,p2,q2): 
	
	# Find the 4 orientations required for 
	# the general and special cases 
	o1 = orientation(p1, q1, p2) 
	o2 = orientation(p1, q1, q2) 
	o3 = orientation(p2, q2, p1) 
	o4 = orientation(p2, q2, q1)

	# print(o1,o2,o3,o4) 

	# General case 
	if ((o1 != o2) and (o3 != o4)): 
		return True

	# Special Cases 

	# p1 , q1 and p2 are colinear and p2 lies on segment p1q1 
	if ((o1 == 0) and onSegment(p1, p2, q1)): 
		return True

	# p1 , q1 and q2 are colinear and q2 lies on segment p1q1 
	if ((o2 == 0) and onSegment(p1, q2, q1)): 
		return True

	# p2 , q2 and p1 are colinear and p1 lies on segment p2q2 
	if ((o3 == 0) and onSegment(p2, p1, q2)): 
		return True

	# p2 , q2 and q1 are colinear and q1 lies on segment p2q2 
	if ((o4 == 0) and onSegment(p2, q1, q2)): 
		return True

	# projection case
	if (o1 != o2) and (o3 == o4):
		return True

	# If none of the cases 
	return False

def perp_dist(p1,p2,p3):
	x0 = p1.x
	y0 = p1.y

	x1 = p2.x
	y1 = p2.y

	x2 = p3.x
	y2 = p3.y

	try:
		dist = abs((((y0-y1)/(x1-x0))*x2 + y2 + (((y1-y0)/(x1-x0))*x0-y0))/math.sqrt(((y0-y1)/(x1-x0))**2+1))
	except:
		dist = abs((((y0-y1)/(1))*x2 + y2 + (((y1-y0)/(1))*x0-y0))/math.sqrt(((y0-y1)/(1))**2+1))

	return dist

def get_intersect_pts(p1,p2,p3,p4):
	x1 = p1.x
	y1 = p1.y

	x2 = p2.x
	y2 = p2.y

	x3 = p3.x
	y3 = p3.y

	x4 = p4.x
	y4 = p4.y

	try:
		m12 = (y2 - y1)/(x2 - x1)
	except:
		m12 = y2 - y1

	try:
		m34 = (y4 - y3)/(x4 - x3)
	except:
		m34 = y4 - y3

	c12 = y1 - (m12 * x1)
	c34 = y3 - (m34 * x3)

	try:
		x_intersect = round((c12 - c34)/(m34 - m12))
	except:
		x_intersect = round(c12 - c34)

	y_intersect = round((m12 * x_intersect) + c12)
	p_intersect = Point(x_intersect, y_intersect)

	return p_intersect

def plain_dist(p1, p2):
	return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)