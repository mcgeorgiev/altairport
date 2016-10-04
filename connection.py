import sqlite3

# class Connection(object):
#     _db_connection = None
#     _db_cur = None

#     def __init__(self):
#         self._db_connection = sqlite3.connect('airportdata.db')
#         self._db_cur = self._db_connection.cursor()

#     def query(self, query, param):
#         return self._db_cur.execute(query, param)

#     def fetchall(self):
#         return self._db_cur.fetchall()

#     def __del__(self):
#        self._db_connection.close()

class Connection(object):
    def __init__(self):
        self.db_name = 'airportdata.db'

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, type, value, traceback):
        self.conn.close()



# db = Connection()

