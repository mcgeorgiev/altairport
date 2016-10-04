from connection import Connection
from math import pow, sqrt
import operator
import json

# sent:
# nearest aiport to the user (location lookup/ postcode)
# destination airports (can be location lookup/ postcode)
# closeness

def get_lat_lon(iata_code):
    with Connection() as conn:
        cur = conn.cursor()
        iata = (iata_code,)
        cur.execute(
            """
            SELECT latitude_deg, longitude_deg
            FROM airports
            WHERE iata_code = ?
        """, iata)
        return cur.fetchall()[0]


def get_near_airports(lat, lon):
    # don't hard code distance
    with Connection() as conn:
        cur = conn.cursor()
        lat_lon = (lat, lat, lon, lon)
        cur.execute(
        """
        select latitude_deg, longitude_deg, iata_code, name
        from airports
        where latitude_deg > (? - 1.3) and latitude_deg < (? + 1.3)
        and longitude_deg > (?-1.3) and longitude_deg < (?+1.3)
        """, lat_lon)
        return [((item[0], item[1]), item[2], item[3]) for item in cur.fetchall()]


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
    def log_and_execute(cursor, sql, *args):
        print sql
        s = sql
        if len(args) > 0:
            # generates SELECT quote(?), quote(?), ...
            cursor.execute("SELECT " + ", ".join(["quote(?)" for i in args]), args)
            quoted_values = cursor.fetchone()
            for quoted_value in quoted_values:
                s = s.replace('?', quoted_value, 1)
        print "SQL command: " + s
        cursor.execute(sql, args)

    with Connection() as conn:
        cur = conn.cursor()
        query = "select airline, source_airport, destination_airport from routes where source_airport in (" + ",".join("?"*len(source)) + ") and destination_airport in (" + ",".join("?"*len(dest)) + ")"
        log_and_execute(cur, query, (source + dest))
        cur.execute(
            "select airline, source_airport, destination_airport from routes where source_airport in (" + ",".join("?"*len(source)) + ") and destination_airport in (" + ",".join("?"*len(dest)) + ")", (source + dest))
        data =  cur.fetchall()
    return data


def verify_routes(valid_routes, nearest_source, nearest_dest):
    json_routes = []
    for route in valid_routes:
        for s_airport in nearest_source:
            for d_airport in nearest_dest:
                if s_airport["iata"] == route[1] and d_airport['iata'] == route[2]:
                    # print route[1], route[2]
                    # create route dictionary should have this in a seperate function
                    r = create_route_json(s_airport, d_airport, route[0])
                    json_routes.append(r)
    return json_routes


def create_route_json(source, dest, airline):
    route = {}
    route["source"] = source
    route["destination"] = dest
    route["airline"] = {}
    route["airline"]["name"] = None
    route["airline"]["code"] = airline
    return route


def create_json(source, source_lat, source_lon, dest, dest_lat, dest_lon, valid_routes):
    # this will have to be changed at some point to stop it being hard coded.

    source_dict = {"data": source, "type": "airport", "lat": source_lat, "lon": source_lon}
    dest_dict = {"data": dest, "type": "airport", "lat": dest_lat, "lon": dest_lon}
    travel_distance_dict = {"source": 0, "dest": 0}

    meta = {"entry":{"source":source_dict, "destination":dest_dict}, "travel_distance_dict": travel_distance_dict}

    return {"meta": meta, "routes": valid_routes}


def get_routes(input):
    # get lat lon by whatever means
    source_entry = input['source']
    source_lat, source_lon = get_lat_lon(source_entry)

    # get close airports
    source_airports = format_airports(get_near_airports(source_lat, source_lon))

    # order them
    nearest_source = get_k_nearest_neighbour((source_lat,source_lon), source_airports)

    # get lat lon by whatever means
    dest_entry = input['destination']
    dest_lat, dest_lon = get_lat_lon(dest_entry)

    # get close airports
    dest_airports = format_airports(get_near_airports(dest_lat, dest_lon))

    # order them
    nearest_dest = get_k_nearest_neighbour((dest_lat,dest_lon), dest_airports)


    # check if routes between them exist
    source_iata_list = [source['iata'] for source in nearest_source]
    dest_iata_list = [dest['iata'] for dest in nearest_dest]
    valid_routes_codes = check_routes(source_iata_list, dest_iata_list)
    print '**********'
    print valid_routes_codes
    # verify_routes
    valid_routes = verify_routes(valid_routes_codes, nearest_source, nearest_dest)

    # create json
    json_dict = create_json(source_entry, source_lat, source_lon, dest_entry, dest_lat, dest_lon, valid_routes)
    JSON = json.dumps(json_dict)
    return JSON

