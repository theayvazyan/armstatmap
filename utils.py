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

        coords.append(all_coords)
    return ids, names, coords


def get_hotels_file():
    with open('arm_hotels.json', encoding="utf8") as f:
        result = json.load(f)['elements']

    names, coords = [], []
    for node in result:
        if node['type'] == 'node':
            if 'name' in node['tags']:
                names.append(node['tags']['name'])
            elif 'name:en' in node['tags']:
                names.append(node['tags']['name:en'])
            elif 'name:de' in node['tags']:
                names.append(node['tags']['name:de'])
            elif 'name:hy' in node['tags']:
                names.append(node['tags']['name:hy'])
            else:
                names.append(None)

            coords.append((float(node['lon']), float(node['lat'])))

    return names, coords

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
                        current_coords.append([float(member['geometry'][i]['lon']), float(member['geometry'][i]['lat'])])
                    all_coords.append(current_coords)

            for i in range(1, len(all_coords)-1):
                c_sc = all_coords[i][0]
                c_ec = all_coords[i][-1]

                p_sc = all_coords[i-1][0]
                p_ec = all_coords[i-1][-1]

                if c_sc != p_sc and c_sc != p_ec and c_ec != p_sc and c_ec != p_ec:
                    print('Found global chaos!!!')
                    for j in range(i+1, len(all_coords)):
                        n_sc = all_coords[j][0]
                        n_ec = all_coords[j][-1]
                        if n_sc == p_sc or n_sc == p_ec or n_ec == p_sc or n_ec == p_ec:
                            all_coords[i], all_coords[j] = all_coords[j], all_coords[i]
                            print('Global chaos fixed!')
                            break

            fixes = True
            while fixes:
                fixes = False
                for i in range(0, len(all_coords)):
                    if i != 0 and all_coords[i][-1] == all_coords[i-1][-1]:
                        all_coords[i].reverse()
                        fixes = True
                        break
                    if i < len(all_coords)-1:
                        if all_coords[i][0] == all_coords[i + 1][-1]:
                            all_coords[i].reverse()
                            fixes = True
                            break

            coords.append(all_coords)
    return ids, names, coords


def statebycoord(searchcoord, stateids, statecoords):
    statecoords = np.array(statecoords)

    statepolies = []
    for l in statecoords:
        flat_list = [item for sublist in l for item in sublist]
        statepolies.append(Polygon(flat_list))

    point = Point(searchcoord[0], searchcoord[1])

    for item in statepolies:
        if point.within(item):
            return stateids[statepolies.index(item)]
    return -1


hnames, hcoords = get_hotels_file()

pids, pnames, pcoords = get_provinces_file()

polys = []

for pcoord in pcoords:
    tmp_item = []
    for cm in pcoord:
        for c in cm:
            tmp_item.append(c)
    polys.append(Polygon(tmp_item))

geopoly = "GEOMETRYCOLLECTION("
for poly in polys:
    geopoly += poly.wkt + ", "
geopoly = geopoly[:-2]
geopoly += ")"

print('that is all')
print(hnames[279])
print(pnames[pids.index(364077)])
print(statebycoord(hcoords[279], pids, pcoords))

print(hnames[0])
print(pnames[pids.index(364087)])
print(statebycoord(hcoords[0], pids, pcoords))
