import win32api, win32con
import time

def click_at_pos(x,y):
	win32api.SetCursorPos((x,y))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
	# time.sleep(0.001)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)