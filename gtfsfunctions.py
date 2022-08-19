import math
from datetime import datetime
import time
import location
from gtfsstatic import GtfsStatic

class GtfsFunctions:
    
    def __init__(self, data_directory, gtfs_directory, position: dict = None):
        self.__data_directory = data_directory
        self.__gtfs_directory = gtfs_directory
        self.gtfs = GtfsStatic(data_directory, gtfs_directory).gtfs
        if position is None:
            self.position = self.get_location() 
        else:
            self.position = position 

    # get current location coordinates from the IOS location module
    def get_location(self):
    	location.start_updates()
    	time.sleep(1)
    	loc = location.get_location()
    	location.stop_updates()
    	if loc:
    		return {'lat': loc['latitude'], 'lon': loc['longitude']}
    
    # Haversine formula
    def distance(self, lat1, lon1, lat2, lon2):  # generally used geo measurement function
        R = 6378.137; # Radius of earth in KM
        dLat = lat2 * math.pi / 180 - lat1 * math.pi / 180
        dLon = lon2 * math.pi / 180 - lon1 * math.pi / 180
        a = (math.sin(dLat/2) * math.sin(dLat/2) +
            math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) *
            math.sin(dLon/2) * math.sin(dLon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = R * c
        return d * 1000; # meters

    def get_time(self):
        now = datetime.now()
        cur_time = now.strftime("%H:%M:%S")
        if cur_time[0] is '0':
            cur_time = cur_time[1:]
        print(cur_time)
        return cur_time
    
    # return 1 (Monday) - 7 (Sunday)
    def get_weekday(self):
        now = datetime.now()
        return now.strftime("%A").lower()
    
    def get_nearest_stops(self, count: int = 1):
        nearest = [None] * count
        stops = self.gtfs['stops'].get_inorder()
        for i in range(count):
            nearest_gps = self.distance(self.position['lat'], self.position['lon'], float(stops[0]['stop_lat']), float(stops[0]['stop_lon']))
            for stop in stops:
                dist = self.distance(self.position['lat'], self.position['lon'], float(stop['stop_lat']), float(stop['stop_lon']))
                if dist < nearest_gps:
                    nearest[i] = stop
                    nearest_gps = dist
            stops.remove(nearest[i])
        return nearest
    
    def get_service_id_by_weekday(self, weekday: str):
        for day in self.gtfs['calendar']:
            if day[weekday] == '1':
                return day['service_id']
    
    def get_trip_id_by_service_id(self, service_id):
        trip_ids = []
        for trip in self.gtfs['trips'].values():
            if trip['service_id'] == service_id:
                trip_ids.append(trip['trip_id'])
        return trip_ids
    
    def get_all_buses_at_stop(self, stop_id):
        return [stop for stop in self.gtfs['stop_times'] if stop_id in stop['stop_id']]
    
    def get_next_bus_at_stop(self, stop_id, trip_ids, cur_time: str, count: int = 1):
        next_buses = []
        last_buses = []
        
        # use i to track last stops
        for stop_time, i in zip(self.gtfs['stop_times'],range(len(self.gtfs['stop_times']),-1,-1)):
            if stop_id in stop_time['stop_id'] and stop_time['arrival_time'] >= cur_time and stop_time['trip_id'] in trip_ids and stop_time not in next_buses:
                next_buses.append(stop_time)
        
        # sort incoming buses by arrival time
        next_buses = sorted(next_buses, key = lambda x: x['arrival_time'])
        
        count = len(next_buses) if count > len(next_buses) else count
        return next_buses[:count]
    
    def print_stops(self, nearest, count=1):
        for i in range(count):
            print('[' + str(i) + '] ' + str(round(self.distance(self.position['lat'], self.position['lon'], float(nearest[i]['stop_lat']), float(nearest[i]['stop_lon'])))) + 'm | '+ nearest[i]['stop_name'] + ' (' + nearest[i]['stop_code'] + ') ' + nearest[i]['stop_lat'] + ',' + nearest[i]['stop_lon'])
    
    def print_stop_times(self, stop_times, count=1):
        trips = self.gtfs['trips']
        stop_time_trips = []
        for stop_time in stop_times:
            stop_time_trips.append(trips[stop_time['trip_id']])
        
        count = len(stop_times) if count > len(stop_times) else count
        for i in range(count):
            print(stop_times[i]['arrival_time'][:len(stop_times[i]['arrival_time'])-3] + ' | ' + stop_time_trips[i]['trip_headsign'])
      
      
    def indices(self, lst, item):
        return [i for i, x in enumerate(lst) if x == item]
       
    def direction(self, destination):
        GtfsFunctions.dest_gtfsf = GtfsFunctions(self.__data_directory, self.__gtfs_directory, destination)
        dest_gtfsf = GtfsFunctions.dest_gtfsf
        weekday = self.get_weekday()
        time = self.get_time()
        today_service_id = self.get_service_id_by_weekday(weekday)
        today_trip_ids = self.get_trip_id_by_service_id(today_service_id)
    
        count = 6
    
        origin_nearest = self.get_nearest_stops(count)
        dest_nearest = dest_gtfsf.get_nearest_stops(count)
        
        next_bus_at_origin = self.get_next_bus_at_stop(origin_nearest[0]['stop_id'], today_trip_ids, time)[0]

        print(time)
        
        matching_stop_times = []
        matching_stop_ids = []
        
        start_stop = []
        
        for stop_time in self.gtfs['stop_times']:
            if (stop_time['stop_id'] == origin_nearest[0]['stop_id'] or stop_time['stop_id'] == dest_nearest[0]['stop_id']) and stop_time['trip_id'] in today_trip_ids and stop_time['trip_id'] in next_bus_at_origin['trip_id']:
                if stop_time['trip_id'] in matching_stop_ids and stop_time['trip_id'] in next_bus_at_origin['trip_id']:
                    matching_stop_ids.append(stop_time['trip_id'])
                    matching_stop_times.append(stop_time)
                    
                    dup_indices = self.indices(matching_stop_ids, matching_stop_ids[-1])
                    start_stop.append((matching_stop_times[dup_indices[0]], matching_stop_times[dup_indices[1]]))
                    
                    matching_stop_times.clear()
                    matching_stop_ids.clear()
                    
                    break
                    
                matching_stop_ids.append(stop_time['trip_id'])
                matching_stop_times.append(stop_time)
        
        
        print(start_stop)
        
        '''
        duplicate = []
        temp = []
        for matching_id in matching_stop_ids:
            for temp_trip in temp:
                if matching_id is not temp_trip and matching_id['trip_id'] == temp_trip['trip_id']:
                    duplicate.append(matching_id)
                    duplicate.append(temp_trip)
            temp.append(matching_id)
            
        print(duplicate[:2])
        '''
