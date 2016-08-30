from connection import db
from math import pow, sqrt

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
    lat_lon = (lat, lat, lon, lon)
    db.query(
        """
        select latitude_deg, longitude_deg, iata_code, name
        from airports
        where latitude_deg > (? - 1) and latitude_deg < (? + 1)
        and longitude_deg > (?-1.0) and longitude_deg < (?+1.0)
        """, lat_lon)
    return [((item[0], item[1]), item[2], item[3]) for item in db.fetchall()]

def get_nearest_airport(home_loc, location_list):
    pass

def euclidean_distance(loc_1, loc_2, length):
    distance = 0
    for x in range(length): # go through both x1-x2 and y1-y2
        distance += pow(loc_1[x]-loc_2[x],2)
    return sqrt(distance)


def get_k_nearest_neighbour(test, train, k=999):
    distances = []
    for item in train:
        dist = euclidean_distance(test, item[0], 2)
        distances.append((dist, item[1], item[2]))
    distances = [item for item in distances if 0.0 not in item]
    distances = sorted(distances)
    try:
        neighbours = distances[:k]
    except:
        neighbours = distances
    return neighbours




def main():
    lat, lon = get_home_lat_lon('LHR')
    location_list = get_home_close(lat, lon)
    print get_k_nearest_neighbour((lat, lon), location_list)

main()






