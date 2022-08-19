import sys
import re
import pickle

class Osmparser:
    def __init__(self, osm_name: str):
        self.filename = osm_name
        
    def parse(self):
        content = []
        try:
            with open(self.filename + '.pk1', 'rb') as f:
                content = pickle.load(f)
        except FileNotFoundError:
            with open(self.filename, 'r', encoding='utf-8') as f:
                for lines in f.readlines():
                    content.append(lines.strip())
            
            with open(self.filename + '.pk1', 'wb+') as f:
                pickle.dump(content, f)
        
        #print('finished reading file')
        return content

    def search(self, query: str):
        content = self.parse()
    
        nodes = dict()
        count = 0
        node_ref = dict()
        node_set = set()
        sets = dict()
    
        for i in range(len(content)):
           if '<tag k=\"name\"' in content[i] and query.lower() in content[i].lower():
                temp = []
                name = re.findall(r'"([^"]*)"', content[i])[1]
                j = 0
                
                while True:
                    if '<node ' in content[i - j]:
                        node_list = re.findall(r'"([^"]*)', content[i - j])
                        #result = '\'' + name + '\': {\'lat\': ' + str(float(node_list[2])) + ', \'lon\': ' + str(float(node_list[4])) + '}, '
                        #print(result, end='')
                        
                        while name in nodes:
                            if name.split(' ')[-1].isdigit():
                                name = ' '.join(str(x) for x in name.split(' ')[:-1]) + ' ' + str(int(name.split(' ')[-1]) + 1)
                            else:
                                name = name + ' 2'
                                
                        nodes[name] = {'lat': float(node_list[2]), 'lon': float(node_list[4])}
                        break
                    elif '<nd ' in content[i - j]:
                        ref = re.findall(r'"([^"]*)', content[i - j])[0]
                        node_set.add(ref)
                        temp.append(int(ref))
                    elif '<way ' in content[i - j]:
                        break
                    j += 1
    
                if temp:
                    sets[name] = temp
                
                count += 1
                if count == 10:
                    break
    
        #print(len(node_set))
                       
                                         
        ref_dict = dict()                  
            
        for line in content:
            if '<node ' in line:
                for element in node_set:
                    if element in line:
                        node_list = re.findall(r'"([^"]*)', line)
                        ref_dict[int(element)] = {'lat': float(node_list[2]), 'lon': float(node_list[4])}
    
        ref_coord = dict()
        '''
        try:
            with open('ref_coord.pk1', 'rb') as f:
                ref_coord = pickle.load(f)
        except FileNotFoundError:
        '''
        for key in sets:
            while key in ref_coord:
                if key in ref_coord:
                    if key.split(' ')[-1].isdigit():
                        ' '.join(str(x) for x in key.split(' ')[:-1]) + ' ' + str(int(key.split(' ')[-1]) + 1)
                    else:
                        key = key + ' 2'
            ref_coord[key] = []
            for ref in sets[key]:       
                ref_coord[key].append(ref_dict[ref])
                
            
        for key in ref_coord:
            lat_sum = 0
            lon_sum = 0
            for each_ref in ref_coord[key]:
                lat_sum += each_ref['lat']
                lon_sum += each_ref['lon']
                
            nodes[key] = {'lat': round(lat_sum/len(ref_coord[key]), 7), 'lon': round(lon_sum/len(ref_coord[key]), 7)}
    
        return nodes
        
        
