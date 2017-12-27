import json
from itertools import groupby

def districts():
    data = json.load(open('/Users/ob4c/redistrict/wageo.json'))
    group = get_group(data)
    groups = partition(group, 4)
    new = label(data, groups)
    json.dump(newdata,open('new.json','w'))
    
def get_coordinates_from_feature(feature):
    if feature['geometry']['type'] == 'Polygon':
        return feature['geometry']['coordinates'][0]
    if feature['geometry']['type'] == 'MultiPolygon':
        return feature['geometry']['coordinates'][0][0]

def get_population_from_feature(feature):
    return feature['properties']['POP10']

def get_coordinate_from_feature(feature):
    coordinates = get_coordinates_from_feature(feature)
    xs,ys = zip(*coordinates)
    return max(xs), max(ys)

def divide(group, ratio):
    population = get_pop(group)*ratio
    axis = get_axis(group)
    group1 = []
    group2 = []
    new_population = 0
    for i,v in axis:
        if new_population < population:
            for block in v:
                group1.append(block)
                new_population += block['p']
        else:
            for block in v:
                group2.append(block)
    return group1, group2

def partition(group, sections):
    if sections == 1:
	    return [group]
    low = sections/2
    ratio = float(low)/sections
    group1, group2 = divide(group, ratio)
    return partition(group1, low) + partition(group2,sections-low)

def get_spread(data, key):
    a = sorted([i[key] for i in data])
    return a[-1]-a[0]

def get_group(data):
    lst = []
    for i,v in enumerate(data['features']):
        p = get_population_from_feature(v)
        x,y = get_coordinate_from_feature(v)
        lst.append({'p':p, 'x':x, 'y':y, 'i':i})
    return lst

def get_axis(group):
    if get_spread(group, 'x') > get_spread(group, 'y'):
        dim = 'x'
    else:
        dim = 'y'
    return groupby(sorted(group,key=lambda x: x[dim]), key=lambda x: x[dim])

def get_pop(group):
    return sum(i['p'] for i in group)

def label(data,groups):
    for i,group in enumerate(groups):
        for block in group:
            data['features'][block['i']]['properties']['group'] = i
            data['features'][block['i']]['style'] = {'fill': 'red' if i==0 else 'blue'}
    return data

