from connection import db
from math import pow, sqrt
from copy import deepcopy


# sent:
# nearest aiport to the user (location lookup/ postcode)
# destination airports (can be location lookup/ postcode)

"""
| enter place/postcode/nearest airport |
------------------------
        |
        V
------------------------
| look up lat/lon      |
------------------------
        |
        V
------------------------
| get airports in that lat/lon|
------------------------
        |
        V
------------------------
|
"""


out = [{"destination": {
            "name": "Glasgow airport",
            "code": "GLA"}}]



def get_home_lat_lon(iata_code):
    iata = (iata_code,)
    db.query(
        """
            SELECT latitude_deg, longitude_deg
            FROM airports
            WHERE iata_code = ?
        """, iata)
    return db.fetchall()[0]


def get_home_close(lat, lon):
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


def euclidean_distance(loc_1, loc_2, length):
    distance = 0
    for x in range(length): # go through both x1-x2 and y1-y2
        distance += pow(loc_1[x]-loc_2[x],2)
    return sqrt(distance)


def get_k_nearest_neighbour(test, train, k=999):
    distances = []
    for item in train:
        dist = euclidean_distance(test, item[0], 2)
        distances.append((dist, item[1], item[2], item[0]))
    # distances = [item for item in distances if 0.0 not in item]
    distances = sorted(distances)
    try:
        neighbours = distances[:k]
    except:
        neighbours = distances
    return neighbours


def get_routes(destination):
    destination = (destination,)
    db.query(
        """
        select airline, source_airport from routes
        where destination_airport = ?;
        """, destination)

    return db.fetchall()


def verify_routes(home_airports, destination):

    all_destinations = get_routes(destination)

    valid_airports = []
    for airport in home_airports:
        for dest in all_destinations:
            if airport == dest[1]:
                valid_airports.append(dest)
    return valid_airports


def add_to_dict(k_list):
    route_list = []
    for item in k_list:
        route = {
                "home": {"iata": None, "name": None, "lat": None, "lon": None},
                "dest": {"iata": None, "name": None, "lat": None, "lon": None},
                "distance": None,
                "airline": None
                }

        route["distance"] = item[0]
        route["dest"]["iata"] = item[1]
        route["dest"]["name"] = item[2]
        route["dest"]["lat"] = item[3][0]
        route["dest"]["lon"] = item[3][1]
        route_list.append(route.copy())
    return route_list


def filter_real_routes(routes_list, valid_airports):
    # Should I create new dictionaries for diffent airlines?
    valid_routes = []
    for data in routes_list:
        airline_list = []
        for item in valid_airports:
            if data["dest"]["iata"] == item[1]:
                airline_list.append(item[0])
        if airline_list != []:
            data["airline"] = airline_list
            valid_routes.append(deepcopy(data))

    return valid_routes


def main():
    destination = 'SSH'

    lat, lon = get_home_lat_lon('SEN')
    location_list = get_home_close(lat, lon)

    k_list = get_k_nearest_neighbour((lat, lon), location_list)
    routes_list = add_to_dict(k_list)
    home_airports = [code[1] for code in k_list]
    valid_airports = verify_routes(home_airports, destination)
    print filter_real_routes(routes_list, valid_airports)


main()
