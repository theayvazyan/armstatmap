import json
import requests
import numpy as np
from shapely.geometry import Point, Polygon


# Saving Overpass API JSON results to files for offline usage

def update_source(source_type="hotels"):
    if source_type == "hotels":
        file_name = "arm_hotels.json"
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
    else:
        file_name = "arm_provinces.json"
        overpass_query = """
            [out:json];
            area[admin_level = 2][int_name = Armenia]->.search;
            (
                rel(area.search)[admin_level=4];
            );
            out
            geom qt;
            """
    overpass_url = "http://overpass-api.de/api/interpreter"
    response = requests.get(overpass_url, params={'data': overpass_query})

    with open(file_name, 'w') as f:
        json.dump(response.json(), f)

    return "Updated!"


def get_hotels_file():  # Parsing hotels from file
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


def get_provinces_file():  # Parsing provinces from file
    ids, names, coords = [], [], []

    with open('arm_provinces.json', encoding="utf8") as f:
        result = json.load(f)['elements']

    for relation in result:
        if relation['type'] == 'relation':
            ids.append(int(relation['id']))
            names.append(relation['tags']['name:en'])

            current_coords, all_coords = [], []

            for member in relation['members']:
                current_coords = []
                if member['type'] != 'node' and member['geometry'] is not None:
                    for i in range(0, len(member['geometry'])):
                        current_coords.append([float(member['geometry'][i]['lon']), float(member['geometry'][i]['lat'])])
                    all_coords.append(current_coords)

            all_coords = coordinate_mess_fixer(all_coords)
            all_coords = border_order_fixer(all_coords)
            coords.append(all_coords)
    return ids, names, coords


def coordinate_mess_fixer(all_coords):  # Fixing border start point and endpoint order
    for i in range(1, len(all_coords) - 1):
        c_sc = all_coords[i][0]
        c_ec = all_coords[i][-1]

        p_sc = all_coords[i - 1][0]
        p_ec = all_coords[i - 1][-1]

        if c_sc != p_sc and c_sc != p_ec and c_ec != p_sc and c_ec != p_ec:
            # Found border problem
            for j in range(i + 1, len(all_coords)):
                n_sc = all_coords[j][0]
                n_ec = all_coords[j][-1]
                if n_sc == p_sc or n_sc == p_ec or n_ec == p_sc or n_ec == p_ec:
                    all_coords[i], all_coords[j] = all_coords[j], all_coords[i]
                    # Border problem fixed
                    break
    return all_coords


def border_order_fixer(all_coords):  # Fixing borders order
    fixes = True
    while fixes:
        fixes = False
        for i in range(0, len(all_coords)):
            if i != 0 and all_coords[i][-1] == all_coords[i - 1][-1]:
                all_coords[i].reverse()
                fixes = True
                break
            if i < len(all_coords) - 1:
                if all_coords[i][0] == all_coords[i + 1][-1]:
                    all_coords[i].reverse()
                    fixes = True
                    break
    return [subp for p in all_coords for subp in p]


def state_by_coord(searchcoord, stateids, statecoords):  # Assigning a province by hotel coordinates
    statecoords = np.array(statecoords)

    statepolies = []
    for item in statecoords:
        statepolies.append(Polygon(item))

    point = Point(searchcoord[0], searchcoord[1])

    for item in statepolies:
        if point.within(item):
            return stateids[statepolies.index(item)]
    return -1

