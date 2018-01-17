import cv2
import numpy as np
import time
from PIL import Image
import pytesseract
import argparse
import os
from ffmpy import FFmpeg
import re


def GetTimestamp(c_frame):
	cap = cv2.VideoCapture('temp_vid/'+str(c_frame)+'.mpg')
	while(cap.isOpened()):
		ret, frame = cap.read()
		if ret == True:
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
			filename = "{}.jpg".format(os.getpid())
			cv2.imwrite(filename, gray)
			text = pytesseract.image_to_string(Image.open(filename))
			os.remove(filename)
			if len(text) > 0:
				m = re.findall("[0-2]{2}:[0-9]{2}:[0-9]{2}:[0-9]{2}", text)
				if len(m) > 0:
					print(m)
					cap.release()
					return (True, m[0])
			time.sleep(0.04)
		else:
			cap.release()
			return (False, 'empty')


def getTimeFromFrameNumber(frame_no, fps):
	f = frame_no % fps
	s = int(frame_no/fps)
	m = int(s/60)
	s = s%60
	h = int(m/60)
	m = m%60
	return (h, m, s, f)


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
		if not os.path.isfile('temp_vid/vid'+str(current_frame)+'.mpg'):
			ff = FFmpeg(inputs={args["video"]: None}, outputs={'temp_vid/'+str(current_frame)+'.mpg':'-ss '+'%02d'%h+':'+'%02d'%m+':'+'%02d'%s+' -codec copy -t 1'})
			ff.run()
		t = GetTimestamp(current_frame)
		print t
		stamp_found = t[0]
		current_frame += fps*5

	cv2.destroyAllWindows()
