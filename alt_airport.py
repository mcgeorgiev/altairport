from connection import db
from math import pow, sqrt
import operator

# sent:
# nearest aiport to the user (location lookup/ postcode)
# destination airports (can be location lookup/ postcode)
# closeness

def get_lat_lon(iata_code):
    iata = (iata_code,)
    db.query(
        """
            SELECT latitude_deg, longitude_deg
            FROM airports
            WHERE iata_code = ?
        """, iata)
    return db.fetchall()[0]


def get_near_airports(lat, lon):
    # don't hard code distance
    lat_lon = (lat, lat, lon, lon)
    db.query(
        """
        select latitude_deg, longitude_deg, iata_code, name
        from airports
        where latitude_deg > (? - 1.3) and latitude_deg < (? + 1.3)
        and longitude_deg > (?-1.3) and longitude_deg < (?+1.3)
        """, lat_lon)
    return [((item[0], item[1]), item[2], item[3]) for item in db.fetchall()]


def format_airports(airports_data):
    airport_list = []
    for item in airports_data:
        airport = {"iata": None, "name": None, "lat": None, "lon": None}
        airport["iata"] = item[1]
        airport["name"] = item[2]
        airport["lat"] = item[0][0]
        airport["lon"] = item[0][1]
        airport_list.append(airport.copy())
    return airport_list


def euclidean_distance(loc_1, loc_2, length):
    distance = 0
    for x in range(length): # go through both x1-x2 and y1-y2
        distance += pow(loc_1[x]-loc_2[x],2)
    return sqrt(distance)


def get_k_nearest_neighbour(test, train, k=999):
    # test = lat, lon of
    # k = number of neighbours wanted
    for item in train:
        item["distance"] = euclidean_distance(test, (item["lat"], item["lon"]), 2)
    sorted_trained = sorted(train, key=operator.itemgetter('distance'))

    try:
        neighbours = sorted_trained[:k]
    except:
        neighbours = sorted_trained
    return neighbours


def check_routes(source, dest):
    db.query(
        "select airline, source_airport, destination_airport from routes where source_airport in (" + ",".join("?"*len(source)) + ") and destination_airport in (" + ",".join("?"*len(dest)) + ")", (source + dest))
    return db.fetchall()


def verify_routes(valid_routes, nearest_source, nearest_dest):
    for route in valid_routes:
        for s_airport in nearest_source:
            for d_airport in nearest_dest:
                if s_airport["iata"] == route[1] and d_airport['iata'] == route[2]:
                    print route[1], route[2]
                    # create route dictionary should have this in a seperate function
                    create_route_json(s_airport, d_airport, route[0])


def create_route_json(source, dest, airline):
    route = {}
    route["source"] = source
    route["destination"] = dest
    route["airline"] = {}
    route["airline"]["name"] = None
    route["airline"]["code"] = airline
    print route


def main():
    # get lat lon by whatever means
    source = 'STN'
    lat, lon = get_lat_lon(source)

    # get close airports
    source_airports = format_airports(get_near_airports(lat, lon))

    # order them
    nearest_source = get_k_nearest_neighbour((lat,lon), source_airports)


    # get lat lon by whatever means
    source = 'SSH'
    lat, lon = get_lat_lon(source)

    # get close airports
    dest_airports = format_airports(get_near_airports(lat, lon))

    # order them
    nearest_dest = get_k_nearest_neighbour((lat,lon), dest_airports)


    # check if routes between them exist
    source_iata_list = [source['iata'] for source in nearest_source]
    dest_iata_list = [dest['iata'] for dest in nearest_dest]
    valid_routes = check_routes(source_iata_list, dest_iata_list)

    # verify_routes
    verify_routes(valid_routes, nearest_source, nearest_dest)


main()
