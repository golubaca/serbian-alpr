import cv2
import urllib
import numpy as np

cap = cv2.VideoCapture("rtsp://root:sec11met03@192.168.188.8/live2.sdp")
bytes = ''
fgbg = cv2.createBackgroundSubtractorMOG2()
kernel = np.ones((8, 8), np.float32) / 64
lock = 0
while True:
    _,frame = cap.read()
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    except:
        pass

    smoothed = cv2.filter2D(gray, -1, kernel)

    fgmask = fgbg.apply(smoothed)

    ret, mask = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY_INV)
    #
    mask_inv = cv2.bitwise_not(mask)

    cv2.imshow("", fgmask)
    cv2.waitKey(1)