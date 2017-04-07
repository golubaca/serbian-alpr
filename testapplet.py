#!/usr/bin/python

import cv2
import numpy as np
import os
import time
import datetime
import urllib
import pynotify
import random
import appindicator
import gtk
import thread






a = appindicator.Indicator('wallch_indicator', '/usr/share/icons/watermelon.png', appindicator.CATEGORY_APPLICATION_STATUS)
a.set_status( appindicator.STATUS_ACTIVE )
m = gtk.Menu()
ci = gtk.MenuItem( 'Ukljuci' )
qi = gtk.MenuItem( 'Quit' )

m.append(ci)
m.append(qi)

a.set_menu(m)
ci.show()
qi.show()
stop = 0

def proccess_zvake():
    print "Krenulo je"
    print "Da da da da da"
    stream=cv2.VideoCapture('http://root:sec11met03@192.168.188.7/video.mjpg')
    print "....Radim"
    #bytes=''
    fgbg = cv2.createBackgroundSubtractorMOG2()

    upozorenje = 0
    locker = 0
    kernel = np.ones((8,8),np.float32)/64

    global stop

    while True:
        print "....Radim"
        if stop:
            print "stop", stop
            break
        #bytes+=stream.read(16384)
        #a = bytes.find('\xff\xd8')
        #b = bytes.find('\xff\xd9')
        #if a!=-1 and b!=-1:

        if locker > 10:
            locker = 0
        elif locker > 0:
            locker +=1
        #jpg = bytes[a:b+2]
        #bytes= bytes[b+2:]
        _,img = stream.read()
        #img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)

        rows,cols,c = img.shape
        si = 140,90,3
        mask = np.zeros(img.shape, dtype=np.uint8)
        roi_corners = np.array([[(940,220),(1080,240), (1080,310), (940,290)]], dtype=np.int32)
        channel_count = img.shape[2]
        ignore_mask_color = (255,)*channel_count
        cv2.fillPoly(mask, roi_corners, ignore_mask_color)
        masked_image = cv2.bitwise_and(img, mask)
        gray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
        fgmask = fgbg.apply(gray)
        ret, mask = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY_INV)

        mask_inv = cv2.bitwise_not(mask)
        smoothed = cv2.filter2D(mask_inv,-1,kernel)
        iii = smoothed[220:310,940:1080]
        hist,bins = np.histogram(iii.ravel(),256,[0,256])

        black, white, cnt1, cnt2 = 0,0,0,0


        for i in range(0,127):
            black += hist[i]
            cnt1+=1
        bl = float(black / 128.0)

        for i in range(128,256):
            white += hist[i]
            cnt2+=1
        wh = float(white / 128.0)

        tresh = ((wh * 100) / (wh+bl))*10

        if tresh > 2 and locker == 0:
            pynotify.init("Zvakari")
            n = pynotify.Notification("UPOZORENJE", "Neko uzima zvake")
            n.show()
            locker += 1



# def activate_stream(item):
#     try:
#         # thread.start_new_thread(proccess_zvake, (item,))
#         t = threading.Thread(target=proccess_zvake)
#         # threads.append(t)
#         t.start()
#     except Exception as e:
#         print e
#     print "Startujem thread"
#     return True
#
# ci.connect('activate', activate_stream)

def quit(item):
        global stop
        print "stop", stop
        stop = 1
        gtk.main_quit()
        exit(0)

qi.connect('activate', quit)

thread.start_new_thread(proccess_zvake, ())

gtk.main()
