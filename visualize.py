import utils
import numpy as np
from pyproj import Proj
from matplotlib import cm
from mathutils import Matrix, Vector
import bpy
import bmesh

def normalize_points(points):
    """Normalize points while preserving aspect ratio"""

    data = np.array(points)

    minX, minY = np.min(data, axis=0)
    maxX, maxY = np.max(data, axis=0)
    rangeX, rangeY = maxX - minX, maxY - minY

    if rangeX > rangeY:
        data[:, 0] = (data[:, 0] - minX - 0.5*rangeX) / rangeX + 0.5
        data[:, 1] = (data[:, 1] - minY - 0.5*rangeY) / rangeX + 0.5
    else:
        data[:, 0] = (data[:, 0] - minX - 0.5*rangeX) / rangeY + 0.5
        data[:, 1] = (data[:, 1] - minY - 0.5*rangeY) / rangeY + 0.5

    return data


names, coords = utils.get_osm()

print("Number of hotels found : {}".format(len(coords)))

# Project coordinates into Mercator projection
p = Proj(init="epsg:3785")  # Popular Visualisation CRS / Mercator
coords = np.apply_along_axis(lambda x: p(*x), 1, coords)

data = normalize_coords(coords)
hist = heatmap_grid(data, sigma_sq=0.00002, n=100)
heatmap_barplot(hist, colormap=cm.viridis)