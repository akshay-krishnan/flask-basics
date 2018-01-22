import cv2
import numpy as np
import time
from PIL import Image
import pytesseract
import argparse
import os
from ffmpy import FFmpeg
import re
import unicodedata
import shutil

def GetTimestamp(c_frame):
	text = pytesseract.image_to_string(Image.open("temp_vid/"+str(c_frame)+".bmp"))
	file = open("logfile.txt", "a")
	if len(text) > 0:
		m = re.findall("[0-2][0-9]:[0-5][0-9]:[0-5][0-9]:[0-9]{2}", text)
		if len(m) > 0:
			return (True, m[0])
		else:
			file.write(text.encode('ascii','ignore')+"\n")
			file.close()
			return (False, 'garbage')
	else:
		return (False, 'empty')


def getTimeFromFrameNumber(frame_no, fps):
	f = frame_no % fps
	s = int(frame_no/fps)
	m = int(s/60)
	s = s%60
	h = int(m/60)
	m = m%60
	s = s+float(f/fps)
	return (h, m, s, f)


def getTimeFirstFrame(stamp, frameno, fps):
	print stamp, type(stamp)
	l = stamp.split(':')
	t = []
	for i in l:
		t.append(int(i))
	h,m,s,f = t
#	fno = frameno - f
	secs = h*3600 + m*60 + s
	print secs
	isecs = secs - (frameno/fps)
	#print fno/fps
	print isecs
	h = isecs/3600
	m = (isecs%3600)/60
	s = (isecs%3600)%60
	# if fno%fps == 0:
	# 	return (h,m,s,0)
	# else:
	# 	return (h,m,s-1,fps-(fno%fps))
	return (h,m,s,f)


if __name__ == '__main__':
	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video", required=True, help="path to input video from which timestamp is to be extracted")
	args = vars(ap.parse_args())

	if not os.path.exists('temp_vid'):
		os.makedirs('temp_vid')
	
	capt = cv2.VideoCapture(args["video"])
	length = int(capt.get(cv2.CAP_PROP_FRAME_COUNT))
	fps = int(capt.get(cv2.CAP_PROP_FPS))
	capt.release()

	global stamp_found
	stamp_found = False

	current_frame = 0
	while(stamp_found is False and current_frame < length):
		h, m, s, f = getTimeFromFrameNumber(current_frame, fps)	
		if not os.path.isfile('temp_vid/'+str(current_frame)+'.bmp'):
			ff = FFmpeg(inputs={args["video"]: None}, outputs={'temp_vid/'+str(current_frame)+'.bmp':'-ss '+'%02d'%h+':'+'%02d'%m+':'+'%02d'%s+' -vframes 1'})
			ff.run()
		t = GetTimestamp(current_frame)
		stamp_found = t[0]
		current_frame += fps*5
	shutil.rmtree('temp_vid/')
	stamp_str=t[1].encode('ascii','ignore')
	print stamp_str, "timestamp of frame number", current_frame-fps*5
	stamp = getTimeFirstFrame(stamp_str, (current_frame-fps*5), fps)
	print stamp, "stamp of first frame"
