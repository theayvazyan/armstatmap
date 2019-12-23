import overpy
import numpy as np
from shapely.geometry import Point, Polygon, LineString
from matplotlib import pyplot as plt
import json


def get_hotels():
    overpass_query = """
    [out:json][timeout:25];
    area[admin_level=2][int_name=Armenia]->.search;
    (  
      node["tourism"="hotel"](area.search);  
    );
    out body;
    >;
    out skel qt;
    """

    api = overpy.Overpass()
    result = api.query(overpass_query)

    names, coords = [], []
    for node in result.nodes:
        if 'name' in node.tags:
            names.append(node.tags['name'])
        elif 'name:en' in node.tags:
            names.append(node.tags['name:en'])
        elif 'name:de' in node.tags:
            names.append(node.tags['name:de'])
        elif 'name:hy' in node.tags:
            names.append(node.tags['name:hy'])
        else:
            names.append(None)

        coords.append((float(node.lon), float(node.lat)))

    return names, coords


def get_provinces():
    ids, names, coords = [], [], []

    overpass_query = """
    [out:json];
    area[admin_level = 2][int_name = Armenia]->.search;
    (
        rel(area.search)[admin_level=4];
    );
    out
    geom qt;
    """
    api = overpy.Overpass()
    result = api.query(overpass_query)

    for relation in result.relations:
        ids.append(relation.id)
        names.append(relation.tags['name:en'])

        prev_coords, current_coords, all_coords = [], [], []

        for member in relation.members:
            prev_coords = current_coords
            current_coords = []
            if member.geometry is not None:
                for i in range(0, len(member.geometry)):
                    if i > 0:
                        if [float(member.geometry[i].lon), float(member.geometry[i].lat)] != all_coords[i-1]:
                            current_coords.append([float(member.geometry[i].lon), float(member.geometry[i].lat)])
                    else:
                        current_coords.append([float(member.geometry[i].lon), float(member.geometry[i].lat)])
                if len(prev_coords)>0 and current_coords[0] != prev_coords[-1]:
                    current_coords.reverse()
                all_coords.append(current_coords)

        all_coords.append(all_coords[0])
        coords.append(all_coords)
    return ids, names, coords


def get_provinces_file():
    ids, names, coords = [], [], []

    with open('arm_provinces.json', encoding="utf8") as f:
        result = json.load(f)['elements']

    for relation in result:
        if relation['type'] == 'relation':
            ids.append(relation['id'])
            names.append(relation['tags']['name:en'])

            prev_coords, current_coords, all_coords = [], [], []

            for member in relation['members']:
                prev_coords = current_coords
                current_coords = []
                if member['type'] != 'node' and member['geometry'] is not None:
                    for i in range(0, len(member['geometry'])):
                        if i > 0 and len(all_coords) > 0:
                            if [float(member['geometry'][i]['lon']), float(member['geometry'][i]['lat'])] != all_coords[-1]:
                                current_coords.append([float(member['geometry'][i]['lon']), float(member['geometry'][i]['lat'])])
                        else:
                            current_coords.append([float(member['geometry'][i]['lon']), float(member['geometry'][i]['lat'])])
                    if len(prev_coords) > 0 and current_coords[0] != prev_coords[0] and current_coords[-1] == prev_coords[-1]:
                        current_coords.reverse()
                    all_coords.append(current_coords)

            all_coords.append(all_coords[0])
            coords.append(all_coords)
    return ids, names, coords


def statebycoord(searchcoord, stateids, statecoords):
    statecoords = np.array(statecoords)
    nstatecoords = []
    for item in statecoords:
        nitem = []
        nitem.append(item[0])
        for i in range(0, len(item)):
            tmp = get_two_closest(item, nitem[-1], nitem)
            if tmp[0] == tuple(nitem[-1]):
                nitem.append(list(tmp[1]))
            else:
                nitem.append(list(tmp[0]))
        nstatecoords.append(nitem)

    statepolies = []
    for item in statecoords:
        item.append(item[0])
        statepolies.append(Polygon(item))

    point = Point(searchcoord[0], searchcoord[1])

    for item in statepolies:
        if point.within(item):
            return stateids[statepolies.index(item)]
    return -1


#hnames, hcoords = get_hotels()

pids, pnames, pcoords = get_provinces_file()

polys = []

for pcoord in pcoords:
    tmp_item = []
    del(pcoord[-1])
    for cm in pcoord:
        for c in cm:
            tmp_item.append(c)
    polys.append(Polygon(tmp_item))

# Shirak, Syuniq, Gexarquniq fixed
print('that is all')
#print(statebycoord(hcoords[279], pids, pcoords))
#print(statebycoord(hcoords[0], pids, pcoords))
