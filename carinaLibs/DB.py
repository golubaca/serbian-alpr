import MySQLdb

class DB(object):
    db = None

    def __init__(self):
        self.user = "metro"
        self.passwd = "metroadmincarina"
        self.database = "carina"

    def connect(self):
        self.db = MySQLdb.connect(host="192.168.198.119",    # your host, usually localhost
                    user=self.user,         # your username
                    passwd=self.passwd,  # your password
                    db=self.database)        # name of the data base

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
