import cv2
import Helper as Helper
import AnalizeFrame
import AnalizePlate
import time
import thread

class IPStream(object):

    def __init__(self, ip_address, username=None, passwd=None, vendor="vivotek", protocol="rtsp", camera_name=None, fps=3, resolution="1024x768"):

        self.ip_address = ip_address
        self.username = username
        self.passwd = passwd
        self.vendor = vendor
        self.protocol = protocol
        self.camera_name = camera_name
        self.fps = fps
        self.resolution = resolution
        self.analize_frame = AnalizeFrame.AnalizeFrame()
        self.analize_plate = AnalizePlate.AnalizePlate()
        self.helper = Helper.Helper()

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
        stream = cv2.VideoCapture(self.helper.generate_url(self.ip_address, self.username, self.passwd, self.vendor, self.protocol,0))
        self.url = self.helper.generate_url(self.ip_address, None, None, self.vendor, self.protocol,0)
        self.proccess(stream)
        # return stream

    def tst(self):
        frame = self.analize_frame.snapshoot(self.helper.generate_url(self.ip_address, self.username, self.passwd, self.vendor, 'snapshoot',0))
        if int(time.time()) % 2:
            plate = self.analize_plate.proccess(cv2.imencode('.jpg', frame)[1].tostring())
            if plate:
                print plate['results']

    def proccess(self, stream):
        ret, frame = stream.read()
        while ret:
            try:
                his = self.analize_frame.calcHist(frame[80:,70:], True)

                if his > 10:
                    thread.start_new_thread(self.tst, ())

                # slika = self.analize_frame.foreground(frame, True, False)
                ret, frame = stream.read()
                cv2.imshow(str(self.ip_address), frame[80:,70:])
                cv2.waitKey(1)

            except (KeyboardInterrupt):
                exit(0)

