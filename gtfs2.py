import zipfile
import re
import pickle
import math
import requests
from datetime import datetime
from google.transit import gtfs_realtime_pb2
from protobuf_to_dict import protobuf_to_dict
import sys
from binarytree import BinaryTree

files = ['agency.txt', 'calendar.txt', 'calendar_dates.txt', 'routes.txt',
         'shapes.txt', 'stops.txt', 'stop_times.txt', 'trips.txt']

def stops_to_binary_tree(gtfs):
    try:
        with open('saved_stops.pk1', 'rb') as f:
            gtfs['stops'] = pickle.load(f)
    except FileNotFoundError:
        print('inserting stops into binarytree')
        tree = BinaryTree()
        for stop in gtfs['stops']:
            sum_of_coordinates = (float(stop['stop_lat']), float(stop['stop_lon']))
            tree.insert(sum_of_coordinates, stop)

        with open('saved_stops.pk1', 'wb+') as f:
            pickle.dump(tree, f)

        gtfs['stops'] = tree
        print('done inserting into binarytree')
        print()

def extract_from_zip():
    gtfs = {}
    try:
        with zipfile.ZipFile('google_transit.zip', 'r') as zf:
            for file in files:
                name = file[:len(file)-4] # filename without the extension
                gtfs[name] = []
                print('Retreiving ' + file)
                with zf.open(file) as f:
                    columns = f.readline().strip().decode().split(',')
                    for line in f:
                        values = {} # an element of gtfs
                        line_list = line.strip().decode()
                        # split on comma outside of quote
                        line = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', line_list)
                        for i in range(len(columns)):
                            values[columns[i]] = line[i]
                        gtfs[name].append(values)
    except FileNotFoundError as e:
        print(e)
        exit(1)

    # convert stops to a binary tree with coordinates as keys
    stops_to_binary_tree(gtfs)

    # save gtfs
    with open('saved_gtfs.pk1', 'wb+') as f:
        pickle.dump(gtfs, f)
    print('done')

def load_gtfs_dict():
    # load gtfs
    try:
        with open('saved_gtfs.pk1', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        extract_from_zip()
        with open('saved_gtfs.pk1', 'rb') as f:
            return pickle.load(f)

def cantor_pairing(a, b):
    a = abs(a)
    b = abs(b)
    result = (1/2)*(a+b)*(a+b+1)+b
    print(result)
    return result

# extract GPS coordinates with a location module
#
# import time
#
# def get_location():
#     location.start_updates()
#     time.sleep(1)
#     loc = location.get_location()
#     location.stop_updates()
#     if loc:
#         return {'lat': loc['latitude'], 'lon': loc['longitude']}

# Haversine formula
def measure(lat1, lon1, lat2, lon2):  # generally used geo measurement function
    R = 6378.137; # Radius of earth in KM
    dLat = lat2 * math.pi / 180 - lat1 * math.pi / 180
    dLon = lon2 * math.pi / 180 - lon1 * math.pi / 180
    a = (math.sin(dLat/2) * math.sin(dLat/2) +
        math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) *
        math.sin(dLon/2) * math.sin(dLon/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d * 1000; # meters

def get_time():
    now = datetime.now()
    return now.strftime("%H:%M:%S")

# return 1 (Monday) - 7 (Sunday)
def get_weekday():
    now = datetime.now()
    return now.strftime("%A").lower()

def get_nearest_stops(gtfs: dict, gcs: dict, count: int = 1):
    nearest = []
    stops = gtfs['stops'].get_inorder()
    for i in range(count):
         nearest.append(stops[min(range(len(stops)), key = lambda i: measure(gcs['lat'], gcs['lon'], float(stops[i]['stop_lat']), float(stops[i]['stop_lon'])))])
         stops.remove(nearest[i])
    return nearest

    # binary tree for the nearest bus
    # nearest = []
    # nearest.append(gtfs['stops'].get_val_from_closest_key((abs(gcs['lat']), abs(gcs['lon']))))
    # stops = gtfs['stops'].get_inorder()
    # stops.remove(nearest[0])
    # for i in range(1, count):
    #      nearest.append(stops[min(range(len(stops)), key = lambda i: measure(gcs['lat'], gcs['lon'], float(stops[i]['stop_lat']), float(stops[i]['stop_lon'])))])
    #      stops.remove(nearest[i])
    # return nearest

def get_service_id_by_weekday(gtfs, weekday: str):
    for day in gtfs['calendar']:
        if day[weekday] == '1':
            return day['service_id']

def get_trip_id_by_service_id(gtfs, service_id):
    return [trip['trip_id'] for trip in gtfs['trips'] if trip['service_id'] == service_id]

def get_all_buses_at_stop(gtfs, stop_id):
    return [stop for stop in gtfs['stop_times'] if stop_id in stop['stop_id']]

def get_next_bus_at_stop(gtfs, stop_id, trip_ids, time: str, count: int = 1):
    next_buses = []
    next_buses = [stop_time for stop_time in gtfs['stop_times'] if stop_id in stop_time['stop_id'] and stop_time['arrival_time'] >= time and stop_time['trip_id'] in trip_ids]
    next_buses = sorted(next_buses, key = lambda x: x['arrival_time'])
    return next_buses[:count]

def fetch_realtime_data(url: str):
    feed = gtfs_realtime_pb2.FeedMessage()
    response = requests.get(url)
    feed.ParseFromString(response.content)
    return protobuf_to_dict(feed)

def print_stops(nearest, gcs, count=1):
    for i in range(count):
        print('[' + str(i) + '] ' + str(round(measure(gcs['lat'], gcs['lon'], float(nearest[i]['stop_lat']), float(nearest[i]['stop_lon'])))) + 'm '+ nearest[i]['stop_name'] + ' (' + nearest[i]['stop_code'] + ') ' + nearest[i]['stop_lat'] + ',' + nearest[i]['stop_lon'])

def print_stop_times(stop_times, count=1):
    for i in range(count):
        print(stop_times[i]['arrival_time'][:len(stop_times[i]['arrival_time'])-3] + ' ' + stop_times[i]['stop_headsign'])


def main():
    start=datetime.now()
    gtfs = load_gtfs_dict()

    # gtfs['stops'].inorder()
    weekday = get_weekday()
    time = get_time()
    today_service_id = get_service_id_by_weekday(gtfs, weekday)
    today_trip_ids = get_trip_id_by_service_id(gtfs, today_service_id)

    # 377 Richmond Ave
    gcs = {'lat': 48.415272, 'lon': -123.330159}

    # uvic bus loop
    # gcs = {'lat': 48.466120, 'lon': -123.308449}

    usr_input = int(sys.argv[1])
    nearest = get_nearest_stops(gtfs, gcs, usr_input)
    print_stops(nearest, gcs, usr_input)
    
    print(datetime.now()-start)

    buses = get_all_buses_at_stop(gtfs, nearest[0]['stop_id'])

    print()
    usr_input_stop = int(input('Select a stop: '))
    usr_input_count = int(input('How many buses would you like to see: '))
    start=datetime.now()
    next_bus = get_next_bus_at_stop(gtfs, nearest[usr_input_stop]['stop_id'], today_trip_ids, time, usr_input_count)
    # print(nearest[0])
    print()
    print_stop_times(next_bus, usr_input_count)

    print(datetime.now()-start)
    # victoria_vehicle_position = 'http://victoria.mapstrat.com/current/gtfrealtime_VehiclePositions.bin'
    # victoria_trip_updates = 'http://victoria.mapstrat.com/current/gtfrealtime_TripUpdates.bin'
    # veh_position: dict = fetch_realtime_data(victoria_vehicle_position)
    # trip_updates: dict = fetch_realtime_data(victoria_trip_updates)

    # for update in trip_updates['entity']:
    #     for i in range(usr_input_count):
    #         if (update['trip_update']['trip']['trip_id'] == next_bus[i]['trip_id'] and update['trip_update']['stop_time_update'][0]['stop_id'] ==  nearest[i]['stop_id']):
    #             print(update)
    #             epoch = update['trip_update']['stop_time_update'][0]['arrival']['time']
    #             print(datetime.fromtimestamp(epoch))


main()
