import cv2
import numpy as np
import urllib

class AnalizeFrame(object):

    def __init__(self, kernel=5):
        self.kernel = kernel
        self.fgbg = cv2.createBackgroundSubtractorMOG2()

    def setKernel(self, kernel):
        self.kernel = kernel

    def toGrayscale(self, image):
        """
        Convert image to grayscale
        :param image: numpy array
        :return: numpy array
        """
        # gray = cv2.cvtColor(image[380:800, 250:1380], cv2.COLOR_BGR2GRAY)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray

    def foreground(self, image, smooth=False, grayscale=False):
        """
        Extract foreground from background
        :param image: 
        :param smooth: 
        :param grayscale: 
        :return: 
        """
        if smooth and grayscale:
            image = self.toGrayscale(image)
            image = self.smooth(image)
        elif smooth:
            image = self.smooth(image)
        elif grayscale:
            image = self.toGrayscale(image)
        fgmask = self.fgbg.apply(image)
        ret, mask = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY_INV)
        mask_inv = cv2.bitwise_not(mask)
        return mask_inv

    def smooth(self,image):
        """
        Smooth image using kernel
        :param image: 
        :return: 
        """
        smoothed = cv2.filter2D(image, -1, np.ones((self.kernel,self.kernel),np.float32)/self.kernel**2)
        return smoothed

    def calcHist(self,image, foreground=False):
        if foreground:
            image = self.foreground(image,True,True)

        hist, bins = np.histogram(image.ravel(), 256, [0, 256])

        black, white= 0, 0

        for i in range(0, 127):
            black += hist[i]
        bl = float(black / 128.0)

        for i in range(128, 256):
            white += hist[i]
        wh = float(white / 128.0)

        thresh = ((wh * 100) / (wh + bl)) * 10
        return thresh

    def snapshoot(self,url):
        # download the image, convert it to a NumPy array, and then read
        # it into OpenCV format
        resp = urllib.urlopen(url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        # return the image
        return image