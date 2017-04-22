import cv2
import Helper as Helper
import AnalizeFrame
import AnalizePlate
import time
import thread
import imutils



class IPStream(object):
    # name=None, ip_address=None, username=None, passwd=None, vendor="vivotek", protocol="rtsp", rotation=0, roi=None, detect_region=None, fps=3, resolution="1024x768"
    def __init__(self, params):

        self.camera_name = params['name']
        self.ip_address = params['ip']
        self.username = params['username']
        self.passwd = params['passwd']
        self.vendor = params['vendor']
        self.protocol = params['protocol']
        self.rotation = params['rotation']
        self.roi = params['roi']
        self.detect_region = params['detectregion']
        self.fps = params['fps']
        self.resolution = params['resolution']
        self.analize_frame = AnalizeFrame.AnalizeFrame()
        self.analize_plate = AnalizePlate.AnalizePlate()
        self.helper = Helper.Helper()

        print "Ime kamere:",self.camera_name

        self.url = self.helper.generate_url(self.ip_address, params['username'], params['passwd'], self.vendor, self.protocol, 1)

    def start(self):
        """
        Create stream object.
        :return: stream
        """

        if self.protocol is "image":
            image = cv2.imread(self.ip_address,1)
            plate = self.analize_plate.proccess(cv2.imencode('.jpg', image)[1].tostring())
            if plate:
                print plate['results']
        else:
            stream = cv2.VideoCapture(self.url)

            self.proccess(stream)
            # return stream

    def tst(self,frame, image):
        try:
            #frame = self.analize_frame.snapshoot(self.helper.generate_url(self.ip_address, self.username, self.passwd, self.vendor, 'snapshoot',0))
            #self.analize_frame.rotate_image(frame,-15)
            name = "/tmp/{}_{}.jpg".format(time.time(),self.ip_address)
            cv2.imwrite(name,frame)
        except Exception as e:
            print "snap:",e
            return False

        try:
            thread.start_new_thread(self.analize_plate.proccess, (image,name,self.ip_address))
        except:
            return False

    def proccess(self, stream):
        ret, jpg = stream.read()
        if ret: print "Connected"
        pause = time.time()
        connCheck = pause
        if self.roi:
            ht = int(self.roi[0]) if self.roi is not '-1' else 0
            hb = int(self.roi[1]) if self.roi is not '-1' else jpg.shape[0]
            wt = int(self.roi[2]) if self.roi is not '-1' else 0
            wb = int(self.roi[3]) if self.roi is not '-1' else jpg.shape[1]
        if self.detect_region:
            dht = int(self.detect_region[0]) if self.detect_region is not -1 else 0
            dhb = int(self.detect_region[1]) if self.detect_region is not -1 else jpg.shape[0]
            dwt = int(self.detect_region[2]) if self.detect_region is not -1 else 0
            dwb = int(self.detect_region[3]) if self.detect_region is not -1 else jpg.shape[1]
        # print dht,dhb,dwt,dwb
        #print "Konektovan na ",self.ip_address
        while ret:
            try:
                if (type(jpg) == type(None)):
                    break
                if self.rotation:
                    jpg = imutils.rotate_bound(jpg, int(self.rotation))
                frame = cv2.resize(jpg, (0, 0), fx=0.1, fy=0.1)
                # jpg = self.analize_frame.adjust_gamma(jpg,0.9)
                # height = frame.shape[0]
                try:
                    # if self.roi:
                    #     his = self.analize_frame.calcHist(frame[self.roi], True)
                    # else:
                    his = self.analize_frame.calcHist(frame, True)
                except:
                    continue
                # print his
                now = time.time()
                # print his
                if his > 10 and now > pause:
                    # print "proccess"
                    pause = now+.2
                    
                    if self.detect_region:
                        thread.start_new_thread(self.tst, (jpg[dht:dhb, dwt:dwb],jpg,))
                    else:
                        thread.start_new_thread(self.tst, (jpg, jpg,))
                    #pass
                
                if int(time.time()) % 40 == 0 and now > connCheck:
                    connCheck=now+2
                    self.helper.connectionNotify(self.camera_name)

                # slika = self.analize_frame.foreground(frame, True, False)

                # if self.roi:
                #     cv2.imshow(str(self.ip_address),
                #                frame[ht:hb, wt:wb])
                #     # int(self.roi[0]):int(self.roi[1]), int(self.roi[2]):int(self.roi[3])
                # else:
                # cv2.imshow(str(self.ip_address), jpg)
                # cv2.waitKey(1)
                ret, jpg = stream.read()
            except KeyboardInterrupt:
                stream.release()
                stream = None
                print "KI exception"
                exit(0)
            except Exception as e:
                print e,"ALL exceptions"
                stream.release()
                stream = None
                break
        stream.release()
        stream = None
        print "Reconecting...", self.ip_address, self.url
        time.sleep(2)
        self.start()

