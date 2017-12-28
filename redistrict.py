import json
from itertools import groupby

def districts(n, bisect):
    data = json.load(open('/Users/ob4c/redistrict-bigfiles/wageo.json'))
    group = get_group(data)
    groups = partition(group, n, bisect)
    new = label(data, groups)
    json.dump(new,open('new2.json','w'))
    return new
    
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

def divide(group, ratio, axis):
    population = get_pop(group)*ratio
    group1 = []
    group2 = []
    new_population = 0
    counter = 0
    for i,v in axis:
        if new_population < population:
            for block in v:
                if counter == 0:
                    print('b1', block['i'])
                    counter += 1
                group1.append(block)
                new_population += block['p']
        else:
            for block in v:
                group2.append(block)
    return group1, group2

def partition(group, sections, bisect):
    print('sections', sections)
    if sections == 1:
	    return [group]
    low = sections//2
    print('low', low)
    ratio = float(low)/sections
    group1, group2 = bisect(group, ratio)
    return partition(group1, low, bisect) + partition(group2,sections-low, bisect)

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

def get_axes(group):
    by_x = sorted(group,key=lambda x: x['x'])
    by_y = sorted(group,key=lambda x: x['y'])
    print('x', by_x[0])
    print('y', by_y[0])
    return groupby(by_x, key=lambda x: x['x']), groupby(by_y, key=lambda x: x['y'])

def get_ratio(group):
    spreads = sorted([get_spread(group, 'x'), get_spread(group, 'y')])
    return spreads[0]/spreads[1]

def naive_bisect(group, ratio):
    axis = get_axis(group)
    return divide(group, ratio, axis)

def optimize_area_bisect(group, ratio):
    a1, a2 = get_axes(group)
    groupings1 = divide(group, ratio, a1)
    min1 = min(map(get_ratio, groupings1))
    print('min1', min1)
    groupings2 = divide(group, ratio, a2)
    min2 = min(map(get_ratio, groupings2))
    print('min2', min2)
    if min1 > min2:
        return groupings1
    else:
        return groupings2

def get_pop(group):
    return sum(i['p'] for i in group)

def label(data,groups):
    for i,group in enumerate(groups):
        print(i, get_pop(group))
        for block in group:
            data['features'][block['i']]['properties']['group'] = i
    return data

