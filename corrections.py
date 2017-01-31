import math
import numpy as np
from affine import Affine


# def euclidean_distance(p1, p2):
#     """euclidean distance between 2 points
#     """
#     y1, x1 = p1
#     y2, x2 = p2
#     return math.sqrt((x2-x1)**2 + (y2-y1)**2)


# def euclidean_direction(p1, p2):
#     """direction between two points
#     """
#     y1, x1 = p1
#     y2, x2 = p2
#     return (x2-x1, y2-y1)


# def latitude_correction_magnitude(dx, dy):
#     """convert direction values to latitude correction magnitude

#     purely horizontal direction results in magnitude of 1 (full correction)
#     purely vertical direction results in magnitude of 0 (no correction)
#     """
#     dx, dy = abs(float(dx)), abs(float(dy))
#     # alternative calculation method
#     #   note: returns 1 when dy and dx are both 0
#     # 1 - (np.arctan2(dy, dx) * 180 / math.pi) / 90
#     if dx == 0:
#         return 0
#     else:
#         return 1 - (np.arctan(dy/dx) * 180/math.pi) / 90


def convert_index_to_coords(index, affine):
    """convert index values to coordinates

    used to converted x,y index of 2d matrix element
    (e.g., a raster) to coordinates (lon, lat) based
    on coordinates represented by top and left of
    matrix as well as pixel size represented by
    each element

    returns centroids of pixels for accurate distance
    calculations using results
    """
    r, c = index

    pixel_size = affine[0]
    xmin = affine[2]
    lon = xmin + pixel_size * (0.5 + c)

    ymax = affine[5]
    lat = ymax - pixel_size * (0.5 + r)

    return (lon, lat)


# def convert_index_to_lat(ix, affine):
#     if not isinstance(ix, int):
#         raise TypeError('Index must be integer')
#     if not isinstance(affine, Affine):
#         raise TypeError('Not a valid affine instance')

#     pixel_size = affine[0]
#     ymax = affine[5]
#     lat = ymax - pixel_size * (0.5 + ix)
#     return lat


# def get_latitude_scale(lat):
#     """get ratio of longitudal measurement at a latitiude relative to equator

#     at the equator, the distance between 0 and 0.008993216 degrees
#     longitude is very nearly 1km. this allows the distance returned
#     by the calc_haversine_distance function when using 0 and 0.008993216
#     degrees longitude, with constant latitude, to server as a scale
#     of the distance between lines of longitude at the given latitude

#     Args
#         lat (int, float): a latitude value
#     Returns
#         ratio (float): ratio of actual distance (km) between two lines of
#                        longitude at a given latitude and at the equator,
#                        when the distance between those lines at the equator
#                        is 1km
#     """
#     p1 = (0, lat)
#     p2 = (0.008993216, lat)
#     ratio = calc_haversine_distance(p1, p2)
#     return ratio


def calc_haversine_distance(p1, p2):
    """calculate haversine distance between two points

    # formula info
    # https://en.wikipedia.org/wiki/Haversine_formula
    # http://www.movable-type.co.uk/scripts/latlong.html

    Args
        p1: tuple of (longitude, latitude) format containing int or float values
        p2: tuple of (longitude, latitude) format containing int or float values
    Returns
        d (float): haversine distance between given points p1 and p2
    """
    lon1, lat1 = p1
    lon2, lat2 = p2
    # km
    radius = 6371.0
    # difference in rads
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = (math.sin(delta_lat/2)**2 + math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) * math.sin(delta_lon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    # km
    d = radius * c
    return d


