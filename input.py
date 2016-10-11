from connection import Connection

class Place(object):

    def __init__(self, input):
        self.input = input
        self.location = []
        self.location_type = ""

    def lookup(self):
        # Case insensitive
        with Connection() as conn:
            cur = conn.cursor()
            input_name = (self.input, self.input)
            cur.execute(
                """
                SELECT name, municipality, iso_country, latitude_deg, longitude_deg
                FROM airports
                WHERE municipality like ? or name like ?
                """, input_name)
            self.location = cur.fetchall()


    def show(self):
        if len(self.location) == 1:
            print self.location
        else:

    def specify(self)



    def get_multiples():
        pass

def main():
    p = Place('glasgow')
    p.lookup()

main()
