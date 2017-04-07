from openalpr import Alpr


class AnalizePlate(object):
    def __init__(self):
        """
        Simple script init, does not require any params.
        """
        self.last_plate = None
        self.alpr = None
        try:
            self.alpr = Alpr("eu", "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
            if not self.alpr.is_loaded():
                print("Error loading OpenALPR")
        except:
            print("Error")

    def proccess(self, img):
        """
        Process the passed image and return the results.
        :param img: numpy array
        :return: array
        """
        self.alpr.set_top_n(7)
        self.alpr.set_default_region("md")

        results = self.alpr.recognize_array(img)
        if results['results']:
            if self.last_plate != results['results'][0]['plate']:
                self.last_plate = results['results'][0]['plate']
                return results
        return False
