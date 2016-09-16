import sqlite3
import urllib2

def create_raw_table():
    db = sqlite3.connect('airportdata.db')
    cur = db.cursor()
    cur.execute(
        """
        CREATE TABLE airportsraw
        (id int,ident varchar,type varchar,name varchar,latitude_deg float,longitude_deg float,elevation_ft float,
        continent varchar,iso_country varchar,iso_region varchar,municipality varchar,scheduled_service varchar,
        gps_code varchar,iata_code varchar,local_code varchar,home_link varchar,wikipedia_link varchar,keywords varchar)

        """)
    # cur.execute(".mode csv")
    # cur.execute(".import airports.csv airportsraw")
    db.commit()
    db.close()


def create_new_table():
    db = sqlite3.connect('airportdata.db')
    cur = db.cursor()
    query = """
            CREATE TABLE airports AS
            SELECT id, name, latitude_deg,
                   longitude_deg, continent,
                   iso_country, iso_region,
                   municipality, iata_code
            FROM airportsraw
            WHERE scheduled_service LIKE 'yes'
            AND type = 'medium_airport' OR type = 'large_airport'"""
    cur.execute(query)
    db.commit()
    db.close()


def get_routes_data():
    routes_data = urllib2.urlopen('https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat')
    with open('routes.csv', 'wb') as output:
        output.write(routes_data.read())


def create_routes_table():
    db = sqlite3.connect('airportdata.db')
    cur = db.cursor()
    cur.execute("CREATE TABLE routes (airline varchar,airline_id int ,source_airport varchar,source_airport_id int ,destination_airport varchar,destination_airport_id int ,codeshare varchar,stops int,equipment varchar)")

    #cur.execute(".mode csv")
    #cur.execute(".import routes.csv routes")
    db.commit()
    db.close()

create_new_table()
