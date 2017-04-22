import os
from openalpr import Alpr
from DB import DB
import shutil
import time
import datetime
from cv2 import imwrite
import urllib


class AnalizePlate(object):
    def __init__(self):
        """
        Simple script init, does not require any params.
        """
        self.last_plate = None
        self.alpr = None
        self.db = DB()
        try:
            self.alpr = Alpr("rs", "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
            if not self.alpr.is_loaded():
                print("Error loading OpenALPR")
        except:
            print("Error")
            return False

    def proccess(self, img, naziv, ip):
        """
        Process the passed image and return the results.
        :param img: numpy array
        :return: array
        """
        self.alpr.set_top_n(7)
        self.alpr.set_detect_region(False)
        #print "[+] Analiziram tablicu"
        try:
            results = self.alpr.recognize_file(naziv)
        except Exception as e:
            print "Analize plate array error:", e
            #exit(0)
            return False

        if results['results']:
            if self.last_plate != results['results'][0]['plate']:
                self.last_plate = results['results'][0]['plate']
                kandidati = ""
                for plate in results['results'][0]['candidates']:
                    try:
                        kandidati += plate['plate'] + ','
                    except Exception as e:
                        print str(e)
                # shutil.copy(naziv, "/home/metro/Programazer/carina-slike/")
                vreme = time.time()
                #im = cv2.imread(naziv)
                obj = datetime.datetime.fromtimestamp(vreme)
                #ime = obj.strftime("%d-%m-%Y %H:%M:%S")
                folder = obj.strftime("%d.%m.%Y")
                ime = "{}_{}".format(time.time(),ip)
                try:
                    path = "/carina/tablice/"
                    if not os.path.exists("{}{}".format(path,folder)):
                        os.makedirs("{}{}".format("/carina/tablice/",folder))
                    imwrite("{}{}/{}.jpg".format("/carina/tablice/",folder,ime), img)
                    #imwrite("/opt/lampp/htdocs/carina-tablice/{}.jpg".format(ime),img)
                except Exception as e:
                    print e
                    return False
                self.addPlate(results['results'][0]['plate'],kandidati,folder+"/"+ime)
                self.notify(folder+"/"+ime, results['results'][0]['plate'])
                self.checkActivePlates(folder+"/"+ime,results['results'][0]['plate'])
                # print naziv, results['results'][0]['plate']
                #return results
        try:
            os.remove(naziv)
        except:
            pass
        return False

    def notify(self,name,plate, active=False):
        try:
            if active:
                urllib.urlopen(
                    "http://localhost:3000/users?name={0}&tablica={1}&alert={2}".format(name, plate, active))
            else:
                urllib.urlopen(
                    "http://localhost:3000/users?name={0}&tablica={1}&alert=0".format(name, plate))
        except:
            pass



    def addPlate(self,tablica,kandidati, naziv):
        try:
            self.db.execute("INSERT INTO test (br_tablice, moguce_tablice,naziv) VALUES ('{}', '{}','{}')".format(
            tablica, kandidati,naziv))
            return True
        except:
            self.db = DB()
            self.db.execute("INSERT INTO test (br_tablice, moguce_tablice,naziv) VALUES ('{}', '{}','{}')".format(
                tablica, kandidati,naziv))
            return True
        return False

    def checkActivePlates(self,ime,plate):
        res = self.db.execute("SELECT * FROM aktuelno WHERE tablica LIKE '%{}%'".format(plate))
        result = res.fetchall()
        # print result
        if len(result) > 0:
            # print "[!]"*5,rezultat[0][1],"[!]"*5
            self.notify(ime,plate,result[0][1],)
