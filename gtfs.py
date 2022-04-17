import math
import gtfs_kit as gk
from pathlib import Path
from datetime import datetime
from datetime import timedelta

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

#Declare the directory path for the GTFS zip file
# path = Path('google_transit.zip')
path = Path('google_transit.zip')

#Read the feed with gtfs-kit
feed = (gk.read_feed(path, dist_units='km'))

#Check which files are part of the zipped GTFS feed
# gk.list_feed(path)

# 377 Richmond Ave
lat = 48.415272
lon = -123.330159

# UVic Bus Loop
# lat = 48.461950
# lon = -123.315976

# usr_input = input('lat,lon: ').split(',')
# lat = float(usr_input[0])
# lon = float(usr_input[1])

stops_list = feed.stops.values.tolist()

nearest = []

for i in range(4):
    nearest.append(stops_list[min(range(len(stops_list)), key = lambda i: measure(lat, lon, float(stops_list[i][4]), float(stops_list[i][5])))])
    print(str(nearest[i][2]) + ': ' + str(nearest[i][4]) + ' ' + str(nearest[i][5]))
    stops_list.remove(nearest[i])

print()

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
weekday = int(now.strftime("%w"))
weekday = 7 if weekday == 0 else weekday

stop_times = feed.stop_times.values.tolist()

calendar = feed.calendar.values.tolist()

service_id = [x for x in calendar if x[weekday] == 1][0][0]

trips = feed.trips.values.tolist()

today_trip_ids = [x[2] for x in trips if x[1] == service_id]

next_buses = []
count = 3

i = 0
for stop in nearest:
    print(str(round(measure(lat, lon, stop[4], stop[5]))) + "m - " + str(stop[2]) + ' (' + str(stop[1]) + ')')
    next_buses = [x for x in stop_times if stop[0] in x[3] and x[1] >= current_time and x[0] in today_trip_ids]
    next_buses = sorted(next_buses, key = lambda x: x[1])
    for next_bus in next_buses:
        print(next_bus[1][:5] + " - " + next_bus[5])
        i += 1
        if (i >= count):
            i = 0
            break
    print()


