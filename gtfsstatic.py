import re
import pickle
import math
import requests
import sys
from binarytree import BinaryTree

files = ['agency.txt', 'calendar.txt', 'calendar_dates.txt', 'routes.txt',
         'shapes.txt', 'stops.txt', 'stop_times.txt', 'trips.txt']

class GtfsStatic:
    
    def __init__(self, data_directory: str, gtfs_directory: str) -> None:
        '''
        data_directory: folder containing all gtfs data and the location that will be used to store data files
        gtfs_directory: folding of the unziped gtfs zip  
        '''
        self.data_directory = data_directory
        self.gtfs_directory = gtfs_directory
        self.gtfs = self.load_gtfs_dict()
    
    def stops_to_bst(self) -> None:
        '''
        converts stops.txt to a BST with the coordinates as the key
        '''
        tree = BinaryTree()
        for stop in self.gtfs['stops']:
            coord = (float(stop['stop_lat']), float(stop['stop_lon'])) # BST key
            tree.insert(coord, stop)
    
        self.gtfs['stops'] = tree # replace list of dict with BST
        
    def trips_to_hash(self) -> None:
        '''
        converts trips.txt to a haspmap with the trip_id as the key
        '''
        self.gtfs['trips'] = sorted(self.gtfs['trips'], key=lambda d: d['trip_id']) # sort by trip_id
       
        ### temp fix for inconsistent last line ###
        if self.gtfs_directory == 'translink':
            self.gtfs['trips'].pop()
       
        temp: dict = {} # buffer dict with trip_id as key
        for trip in self.gtfs['trips']:
            temp[trip['trip_id']] = trip # insertion
        
        self.gtfs['trips'] = temp # replace list of trips with hashmap
    
    def extract_from_zip(self) -> None:
        '''
        !!!THIS VERSION REQUIRES THE GTFS ZIP FILE TO BE UNZIP PRIOR TO THE PARSING!!!
        
        parases GTFS static data into a list of list of dict      
        for example:
            
            stops.txt and trip.txt 
            each containing 3 entries (excluding the headers) will be parsed into the following structure:
            [[{},{},{}],[{},{},{}]]
            
        inside each dict, each column heading will be a key to its respective values
        for example: 
            
            stop_id,stop_code,stop_name
            1234,987654321,Henderson at Richmond
            
            will be parsed into the following dict:
            {'stop_id':'1234', 'stop_code':'987654321', 'stop_name':'Henderson at Richmond'}
            
        'arrival_time' and 'departure_time' values that lead with '0' or ' ', such as '08:30:00' will have 
        its leading '0' or ' ' removed and the resulting time from the example will be '8:30:00'
        
        the files to be parsed inside the GTFS directory is determined by the files global list
        
        this function is currently also responsible for the conversion of specific gtfs .txt files
        into specific ADT, the resulting ADT will replace the list inside self.gtfs
        
        this function is currently also responsible for the file storage of the self.gtfs variable 
        by pickle dump
        '''
        self.gtfs = {}
        try:
            for file in files:
                name = file[:len(file)-4] # filename without the extension
                self.gtfs[name] = []
                with open(self.data_directory + '/' + self.gtfs_directory + '/' + file, 'r') as f:
                    columns = f.readline().strip().split(',') # headers as 
                    for line in f:
                        values = {} # an element of gtfs
                        line_list = line.strip() # remove leading and trailing spaces
                        
                        # split only on commas that are outside of quotes
                        line = re.split(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', line_list)
                        
                        # the amount of values in the line does not match the amount of headers
                        if len(columns) != len(line):
                            continue

                        for i in range(len(columns)):
                            
                            # remove leading '0' or ' ' from time for consistent time processing
                            if ((columns[i] == 'arrival_time' or columns[i] == 'departure_time') and (line[i][0] == '0' or line[i][0] == ' ')):
                                line[i] = line[i][1:] # exclude first character
                            
                            values[columns[i]] = line[i]
                        self.gtfs[name].append(values)
                        
        except FileNotFoundError as e: # a GTFS file does not exist
            print(self.gtfs_directory + ' not found')
            exit(1)
        
        # ADT conversions
        self.stops_to_bst()
        self.trips_to_hash()
        
        # save gtfs into a file
        with open(self.data_directory + '/' + self.gtfs_directory + '_saved_gtfs.pk1', 'wb+') as f:
            pickle.dump(self.gtfs, f)
    
    def load_file(self, filename: str) -> list:
        '''
        loads a specific pickle file if it exists
           
        filename: pickle file to be loaded inside the data directory
        '''
        try:
            with open(self.data_directory + '/' + filename + '.pk1', 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
                print(filename + ' not found')
                return None
    
    def load_gtfs_dict(self) -> None:
        '''
        attempts to load the gtfs pickle file, if it does not exist, call function in attempt parse and produce the file
        '''
        # load gtfs
        try:
            with open(self.data_directory + '/' + self.gtfs_directory + '_saved_gtfs.pk1', 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            self.extract_from_zip()
            with open(self.data_directory + '/' + self.gtfs_directory + '_saved_gtfs.pk1', 'rb') as f:
                return pickle.load(f)
