import cv2
from openalpr import Alpr
import MySQLdb
import numpy as np
import time
import datetime
import thread
import os
from PyQt4 import QtCore, QtGui
from collections import deque


class DB(object):
    db = None

    def __init__(self):
        self.user = "root"
        self.passwd = ""
        self.db = "carina"

    def connect(self):
        self.db = MySQLdb.connect(host="127.0.0.1",  # your host, usually localhost
                                  user=self.user,  # your username
                                  passwd=self.passwd,  # your password
                                  db=self.db)  # name of the data base

        # self.cursor = self.db.cursor()
        print "[+] Uspesna konekcija"

    def execute(self, sql):
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()
        except (AttributeError, MySQLdb.OperationalError):
            self.connect()
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()
        return cursor


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class PhotoViewer(QtGui.QGraphicsView):
    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self.added = False
        self._zoom = 0
        self._scene = QtGui.QGraphicsScene(self)
        self._photo = QtGui.QGraphicsPixmapItem()

        self._scene.addItem(self._photo)

        self.setScene(self._scene)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))

    def setPhoto(self, pixmap=None, addText=False):
        if pixmap and not pixmap.isNull():
            self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
            if addText:
                font = QtGui.QFont()
                font.setFamily('Lucida')
                font.setFixedPitch(True)
                font.setPointSize(20)
                try:
                    self._scene.removeItem(self._text)
                except:
                    pass
                self._text = QtGui.QGraphicsSimpleTextItem()
                self._text.setText(str(addText))
                self._text.setFont(font)
                self._scene.addItem(self._text)
            self.rect = QtCore.QRectF(self._photo.pixmap().rect())
            if self.added is False:
                self.added = True
                while self.fitInView(self.rect):
                    break
        else:
            self.setDragMode(QtGui.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())

    def zoomFactor(self):
        return self._zoom

    def wheelEvent(self, event):

        if not self._photo.pixmap().isNull():
            if event.delta() > 0:
                factor = 1.35
                self._zoom += 1
            else:
                factor = 0.7
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
                pass
            elif self._zoom == 0:
                self.fitInView(self.rect)
            else:
                self._zoom = 0

    def resizeEvent(self, event):
        try:
            self.fitInView(self.rect)
        except:
            pass


class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.resize(1198, 651)

        self.font = cv2.FONT_ITALIC

        self.image = None
        self.db = DB()
        self.cursor = None
        self.alpr = None
        try:
            self.alpr = Alpr("rs", "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
            if not self.alpr.is_loaded():
                print("Error loading OpenALPR")
        except:
            print "ALPR IMPORT Error"

        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.graphicsView_3 = PhotoViewer(self)
        self.graphicsView_3.setObjectName(_fromUtf8("graphicsView_3"))
        self.gridLayout.addWidget(self.graphicsView_3, 5, 1, 1, 1)
        self.graphicsView_4 = PhotoViewer(self)
        self.graphicsView_4.setObjectName(_fromUtf8("graphicsView_4"))
        self.gridLayout.addWidget(self.graphicsView_4, 5, 0, 1, 1)
        self.graphicsView_2 = PhotoViewer(self)
        self.graphicsView_2.setObjectName(_fromUtf8("graphicsView_2"))
        self.gridLayout.addWidget(self.graphicsView_2, 5, 2, 1, 1)
        self.graphicsView_0 = PhotoViewer(self)
        self.graphicsView_0.setObjectName(_fromUtf8("graphicsView_0"))
        self.gridLayout.addWidget(self.graphicsView_0, 3, 2, 1, 1)
        self.graphicsView_1 = PhotoViewer(self)
        self.graphicsView_1.setObjectName(_fromUtf8("graphicsView_1"))
        self.gridLayout.addWidget(self.graphicsView_1, 4, 2, 1, 1)
        self.graphicsView = PhotoViewer(self)
        self.gridLayout.addWidget(self.graphicsView, 3, 0, 2, 2)
        self.testtext = QtGui.QLabel(self.graphicsView)
        self.testtext.setText("Test")
        self.gridLayout.addWidget(self.testtext)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def setup_camera(self):
        """Initialize camera.
        """
        self.passed_images = deque([])
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.display_video_stream)
        # Display video stream every 100 ms, limit to 10 fps (for testing),
        # can be more
        thread.start_new_thread(self.CaptureImages, ("http://root:sec11met@192.168.188.196/mjpg/video.mjpg",))
        # thread.start_new_thread(self.proccess_images, ())
        self.timer.start(300)

    def display_video_stream(self):

        try:
            i = self.image
            image = QtGui.QImage(i.data, i.shape[1], i.shape[0],
                                 i.strides[0], QtGui.QImage.Format_RGB888)

            img = QtGui.QPixmap(image)
            self.graphicsView.setPhoto(img)
        except Exception as e:
            print e
            pass

        for e, image in enumerate(list(self.passed_images)):
            try:
                im = QtGui.QImage(image[0], image[0].shape[1], image[0].shape[0], image[0].strides[0],
                                  QtGui.QImage.Format_RGB888)
                # img = QtGui.QPixmap.fromImage(im)
                img = QtGui.QPixmap(im)

                if e == 0:
                    self.graphicsView_0.setPhoto(img, image[1])
                if e == 1:
                    self.graphicsView_1.setPhoto(img, image[1])
                if e == 2:
                    self.graphicsView_2.setPhoto(img, image[1])
                if e == 3:
                    self.graphicsView_3.setPhoto(img, image[1])
                if e == 4:
                    self.graphicsView_4.setPhoto(img, image[1])
            except Exception as e:
                print e
                continue

    def proccess_images(self, slika, text):
        try:
            if len(self.passed_images) > 4:
                self.passed_images.rotate(1)
                self.passed_images[0] = [slika, text]
            else:
                self.passed_images.append([slika, text])
        except:
            pass

    def calculate(self,naziv, slika):
        print "CALCULATE"
        try:
            #cv2.imwrite(naziv, slika)

            self.alpr.set_top_n(7)
            self.alpr.set_detect_region(False)
            # print "cao"
            # exit(0)
            try:
                results = self.alpr.recognize_file(naziv)
            except:
                print "Ovde me jebe"
                exit(0)

            if results['results']:
                # im = cv2.imread(naziv)
                tab = results['results'][0]['plate']
                if tab[0:2] == "BG" and tab[2] == "8":
                    tab = ''.join(a[0:2] + "8" + a[3:])
                cv2.putText(slika, tab, (1050, 50), self.font, 1, (0, 255, 0), 3, cv2.LINE_AA)


                now = time.time()
                # slsave = cv2.cvtColor(slika, cv2.COLOR_BGR2RGB)
                cv2.imwrite("/opt/lampp/htdocs/tmp/" + str(now) + ".jpg", slika)

                # urllib.urlopen("http://localhost:3000/users?name={0}&tablica={1}".format(now,results['results'][0]['plate']))
                vr = time.time()
                vre = datetime.datetime.fromtimestamp(vr)
                vreme = vre.strftime('%d-%m-%Y %H:%M:%S')


                # kandidati = ""
                # for plate in results['results'][0]['candidates']:
                #     try:
                #         kandidati += plate['plate'] + ','
                #     except Exception as e:
                #         print str(e)

                # self.image[1] = slika


                #print results['results'][0]['plate'], kandidati
                # try:
                #     self.db.execute("INSERT INTO tablice (br_tablice, moguce_tablice) VALUES ('{}', '{}')".format(results['results'][0]['plate'], kandidati))
                #     '''
                #     sql = "SELECT * FROM aktuelno WHERE tablica LIKE '%{}%'".format(results['results'][0]['plate'])
                #     res = self.db.execute(sql)
                #     rezultat = res.fetchall()

                #     if len(rezultat) > 0:
                #         print "[!]"*5,rezultat[0][1],"[!]"*5
                #         try:
                #             thread.start_new_thread( proccess_images, () )
                #         except:
                #             print "Threading problem"
                #     '''

                # except Exception as e:
                #     print "[!] Carina 2: " + str(e)
                #     self.db = DB()
                self.proccess_images(slika, results['results'][0]['plate'])
            os.remove(naziv)
        except Exception as e:
            print "ERROR 001", str(e)

    def get_car(self):
        fgbg = cv2.createBackgroundSubtractorMOG2()
        kernel = np.ones((8, 8), np.float32) / 64
        lock = 0
        while 1:
            #     continue


            if not lock:
                lock = 1
                try:
                    gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
                except:
                    pass
                smoothed = cv2.filter2D(gray[380:800, 250:1380], -1, kernel)

                ##################

                fgmask = fgbg.apply(smoothed)

                ret, mask = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY_INV)

                mask_inv = cv2.bitwise_not(mask)

                hist, bins = np.histogram(mask_inv.ravel(), 256, [0, 256])

                black, white, cnt1, cnt2 = 0, 0, 0, 0

                for i in range(0, 127):
                    black += hist[i]
                    cnt1 += 1
                bl = float(black / 128.0)

                for i in range(128, 256):
                    white += hist[i]
                    cnt2 += 1
                wh = float(white / 128.0)

                tresh = ((wh * 100) / (wh + bl)) * 10

                if tresh > 2:
                    naziv = "/tmp/" + str(time.time()) + "_carina2.jpg"
                    cv2.imwrite(naziv, self.image[380:800, 250:1380])  # [120:500, 250:1100]
                    try:
                        # cv2.imwrite("/tmp/"+str(time.time())+"0000.jpg", frame)
                        thread.start_new_thread(self.calculate, (naziv, self.image,))
                    except:
                        print "Threading problem"
                    time.sleep(0.1)
                    # cv2.imshow('video', mask_inv)


                    # if cv2.waitKey(1) == 27:
                    #   break
            else:
                lock = 0
                # cv2.imshow('video', frame)

    def CaptureImages(self, url):
        cap = cv2.VideoCapture(url)

        start = 0
        lock = 0
        fgbg = cv2.createBackgroundSubtractorMOG2()
        kernel = np.ones((8, 8), np.float32) / 64
        while True:
            _,frame = cap.read()
            self.image = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)


                #     continue


            if not lock:
                lock = 1
                try:
                    gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
                except:
                    pass
                smoothed = cv2.filter2D(gray[380:800, 250:1380], -1, kernel)

                ##################

                fgmask = fgbg.apply(smoothed)

                ret, mask = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY_INV)

                mask_inv = cv2.bitwise_not(mask)

                hist, bins = np.histogram(mask_inv.ravel(), 256, [0, 256])

                black, white, cnt1, cnt2 = 0, 0, 0, 0

                for i in range(0, 127):
                    black += hist[i]
                    cnt1 += 1
                bl = float(black / 128.0)

                for i in range(128, 256):
                    white += hist[i]
                    cnt2 += 1
                wh = float(white / 128.0)

                tresh = ((wh * 100) / (wh + bl)) * 10

                if tresh > 2:
                    naziv = "/tmp/" + str(time.time()) + "_carina2.jpg"
                    cv2.imwrite(naziv, self.image[380:800, 250:1380])  # [120:500, 250:1100]
                    print "CAPTURE"
                    try:
                        # cv2.imwrite("/tmp/"+str(time.time())+"0000.jpg", frame)
                        thread.start_new_thread(self.calculate, (naziv, self.image,))
                    except:
                        print "Threading problem"
                    time.sleep(0.1)
                    # cv2.imshow('video', mask_inv)


                    # if cv2.waitKey(1) == 27:
                    #   break
            else:
                lock = 0
                # cv2.imshow('video', frame)

                    #
        #     try:
        #         _, frame = cap.read()
        #         jpg = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #
        #         self.image = jpg
        #         if start == 0:
        #             thread.start_new_thread(self.get_car, ())
        #             start += 1
        #     except Exception as e:
        #         continue

    def retranslateUi(self):
        self.setWindowTitle(_translate("Carina", "Carina", None))


if __name__ == "__main__":
    import sys
    import sip

    app = QtGui.QApplication(sys.argv)
    app.setStyle("CleanLooks")
    window = Window()
    window.showMaximized()
    window.setup_camera()
    window.show()
    sys.exit(app.exec_())