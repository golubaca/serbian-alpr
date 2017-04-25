import MySQLdb
import ConfigParser

config = ConfigParser.ConfigParser()
config.read(".carinaConfig.ini")


class DB(object):
    db = None

    def __init__(
        self, username=config.get(
            'database', 'username'), passwd=config.get(
            'database', 'password'), database=config.get(
                'database', 'database'), host=config.get(
                    'database', 'host')):
        self.user = username
        self.passwd = passwd
        self.database = database
        self.host = host

    def connect(self):
        self.db = MySQLdb.connect(host=self.host,    # your host, usually localhost
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
