import sqlite3

class Connection(object):
    def __init__(self):
        self.db_name = 'airportdata.db'

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        print 'Entered'
        return self.conn

    def __exit__(self, type, value, traceback):
        print 'Exited'
        self.conn.close()


