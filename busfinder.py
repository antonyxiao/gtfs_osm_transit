from gtfsfunctions import GtfsFunctions
from osmparser import Osmparser
import sys

#parse = Osmparser('map')

while True:
    '''
    results = parse.search(input('Search: '))
    print()
    
    i = 0
    for key in results:
        print('[' + str(i) + '] - ' + key)
        i += 1
    
    print()
    choice = int(input('Select a location: '))
    count = int(input('How many stops would you like to see: '))
    print()
    
    gcs = {}
    
    i = 0
    for key in results:
        if i == choice:
            gcs = results[key]
        i += 1
'''
    count = 10
    # 377 Richmond Ave
    # gcs = {'lat': 48.415272, 'lon': -123.330159}
    
    # uvic bus loop
    # gcs = {'lat': 48.466120, 'lon': -123.308449}
    
    gtfsf = GtfsFunctions('data', sys.argv[1])
    weekday = gtfsf.get_weekday()
    time = gtfsf.get_time()
    today_service_id = gtfsf.get_service_id_by_weekday(weekday)
    today_trip_ids = gtfsf.get_trip_id_by_service_id(today_service_id)
    
    nearest = gtfsf.get_nearest_stops(count)
    gtfsf.print_stops(nearest, count)
    
    # select incoming buses at selected stop
    print()
    usr_input_stop = int(input('Select a stop: '))
    usr_input_count = int(input('How many buses would you like to see: '))
            
    next_bus = gtfsf.get_next_bus_at_stop(nearest[usr_input_stop]['stop_id'], today_trip_ids, time, usr_input_count)
    print()
    gtfsf.print_stop_times(next_bus, usr_input_count)
    
    print()
