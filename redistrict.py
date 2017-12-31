import json
from itertools import groupby
from operator import itemgetter

def districts(n, bisect, outfile):
    geojson = json.load(open('/Users/ob4c/redistrict-bigfiles/wageo.json'))
    new = label(geojson, groups(initial_group(geojson), n, bisect))
    json.dump(new, open(outfile,'w'))
    return new
    
def coordinates(feature):
    if feature['geometry']['type'] == 'Polygon':
        return feature['geometry']['coordinates'][0]
    if feature['geometry']['type'] == 'MultiPolygon':
        return feature['geometry']['coordinates'][0][0]

def coordinate(feature):
    xs, ys = zip(*coordinates(feature))
    return max(xs), max(ys)

def bisection(group, ratio, axis):
    threshold = population(group)*ratio
    group1 = []
    group2 = []
    for i, v in axis:
        if threshold > 0:
            for block in v:
                group1.append(block)
                threshold -= block['p']
        else:
            for block in v:
                group2.append(block)
    return group1, group2

def groups(group, sections, bisect):
    if sections == 1:
	    return [group]
    low = sections//2
    ratio = float(low)/sections
    group1, group2 = bisect(group, ratio)
    return groups(group1, low, bisect) + groups(group2,sections-low, bisect)

def span(group, dimension):
    a = sorted([i[dimension] for i in group])
    return a[-1]-a[0]

def initial_group(geojson):
    lst = []
    for i,v in enumerate(geojson['features']):
        p = v['properties']['POP10']
        x,y = coordinate(v)
        lst.append({'p':p, 'x':x, 'y':y, 'i':i})
    return lst

def axis(group, dim):
    k = itemgetter(dim)
    return groupby(sorted(group, key=k), key=k)

def longest_axis(group):
    if span(group, 'x') > span(group, 'y'):
        dimension = 'x'
    else:
        dimension = 'y'
    return axis(group, dimension)

def axes(group):
    return axis(group, 'x'), axis(group, 'y')

def squareness(group): # 0-1, 0 least square, 1 is most square
    spans = sorted([span(group, 'x'), span(group, 'y')])
    return spans[0]/spans[1]

def naive_bisection(group, ratio):
    return bisection(group, ratio, longest_axis(group))

def optimize_area_bisection(group, ratio):
    axis1, axis2 = axes(group)
    groupings1 = bisection(group, ratio, axis1)
    min1 = min(map(squareness, groupings1))
    groupings2 = bisection(group, ratio, axis2)
    min2 = min(map(squareness, groupings2))
    if min1 > min2:
        return groupings1
    else:
        return groupings2

def population(group):
    return sum(i['p'] for i in group)

def label(geojson, groups):
    for i,group in enumerate(groups):
        print(i, population(group))
        for block in group:
            geojson['features'][block['i']]['properties']['group'] = i
    return geojson
