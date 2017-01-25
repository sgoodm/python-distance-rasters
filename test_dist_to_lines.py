

import fiona
import rasterio
from rasterio import features
from affine import Affine



def rasterize_geom(geom, shape, affine, all_touched=False):
    geoms = [(geom, 1)]
    rv_array = features.rasterize(
        geoms,
        out_shape=shape,
        transform=affine,
        fill=0,
        all_touched=all_touched)
    return rv_array



new_affine = Affine(pixel_size, 0, topleftlon,
                0, -pixel_size, topleftlat)

new_shape = (shape[0]*scale, shape[1]*scale)

rv_array = rasterize_geom(geom, new_shape, new_affine, all_touched=all_touched)




latitude_scale = [
                get_latitude_scale(fsrc_affine[5] - fsrc_affine[0] * (0.5 + i))
                for i in range(fsrc_shape[0])
            ]

feature_stats['mean'] = float(
                            np.sum((masked.T * latitude_scale).T) /
                            np.sum(latitude_scale * (masked.shape[1] - np.sum(masked.mask, axis=1))))



# from scipy import spatial
# from scipy.spatial import KDTree as kdt

# from scipy import spatial
# from scipy.spatial import distance


import numpy as np
import math

import distance


def euclidean_distance(p1, p2):
    """euclidean distance between 2 points
    """
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2-x1)**2 + (y2-y1)**2)


def euclidean_direction(p1, p2):
    """direction between two points
    """
    x1, y1 = p1
    x2, y2 = p2
    return (x2-x1, y2-y1)


def latitude_correction_magnitude(dx, dy):
    """convert direction values to latitude correction magnitude

    purely horizontal direction results in magnitude of 1 (full correction)
    purely vertical direction results in magnitude of 0 (no correction)
    """
    dx, dy = abs(float(dx)), abs(float(dy))
    # alternative calculation method
    #   note: returns 1 when dy and dx are both 0
    # 1 - (np.arctan2(dy, dx) * 180 / math.pi) / 90
    if dx == 0:
        return 0
    else:
        return 1 - (np.arctan(dy/dx) * 180/math.pi) / 90


def index_to_coords(left, top, ix, iy, pixel_size):
    """convert index values to coordinates

    used to converted x,y index of 2d matrix element
    (e.g., a raster) to coordinates (lon, lat) based
    on coordinates represented by top and left of
    matrix as well as pixel size represented by
    each element

   returns centroids of pixels for accurate distance
    calculations using results
    """
    lon = left + pixel_size * (ix + 0.5)
    lat = top - pixel_size * (iy + 0.5)
    return (lon, lat)





def get_latitude_scale(lat):
    """get ratio of longitudal measurement at a latitiude relative to equator

    at the equator, the distance between 0 and 0.008993216 degrees
    longitude is very nearly 1km. this allows the distance returned
    by the calc_haversine_distance function when using 0 and 0.008993216
    degrees longitude, with constant latitude, to server as a scale
    of the distance between lines of longitude at the given latitude

    Args
        lat (int, float): a latitude value
    Returns
        ratio (float): ratio of actual distance (km) between two lines of
                       longitude at a given latitude and at the equator,
                       when the distance between those lines at the equator
                       is 1km
    """
    p1 = (0, lat)
    p2 = (0.008993216, lat)
    ratio = calc_haversine_distance(p1, p2)
    return ratio


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

    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (math.sin(delta_lat/2)**2 + math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) * math.sin(delta_lon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    # km
    d = radius * c

    return d





# x = np.random.randint(2, size=(int(180/10), int(360/10)))
# x = np.random.randint(2, size=(10, 20))

pixel_size = 0.1
x = np.random.choice([0, 1], size=(int(180/pixel_size), int(360/pixel_size)), p=[.8, .2])


# xmin = 10
# xmax = 30 
# ymin = 30
# ymax = 40
# bnds = [xmin, ymin, xmax, ymax]


max_dist = 40

# x = np.array([
#     [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
#     [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1],
#     [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0],
#     [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
# ])

nrows, ncols = x.shape



# print x
print x.shape
print nrows * ncols



z = np.empty(x.shape, dtype=float)


import time
for r in range(nrows):
    trow_start = int(time.time())
    for c in range(ncols):

        cur_index = (r, c)
        print cur_index

        rleft = r-max_dist if r>=max_dist else 0
        rright = r+max_dist if r<=nrows-max_dist else nrows
        cleft = c-max_dist if c>=max_dist else 0
        cright = c+max_dist if c<=ncols-max_dist else ncols
        print rleft, rright, cleft, cright

        x1 = x[rleft:rright, cleft:cright]
        print x1

        # actual_indexes = 

        y = np.ma.masked_array(x1, mask=(x1==0))
        print y

        line_prep = np.ma.nonzero(y)
        line_indexes = zip(line_prep[0], line_prep[1])
        print len(line_indexes)
        # print line_indexes

        if len(line_indexes) == 0:
            z[r][c] = -1
            continue

        # from timeit import timeit
        # print timeit(lambda: [euclidean_distance(cur_index, tmp_index) for tmp_index in line_indexes], number=10000)
        # print timeit(lambda: distance.cdist([cur_index], line_indexes, 'euclidean')[0], number=10000)
        # raise
        # dist_list = [euclidean_distance(cur_index, tmp_index) for tmp_index in line_indexes]
        dist_list = distance.cdist([cur_index], line_indexes, 'euclidean')[0]
        min_dist = min(dist_list)
        min_dist_index = np.where(dist_list == min_dist)
        print min_dist
        print min_dist_index
        # print dist_list
        min_index = line_indexes[min_dist_index[0][0]]
        print min_index
        # for i in min_dist_index:
            # print line_indexes[i]
        # print '---'


        dx, dy = euclidean_direction(cur_index, min_index)
        print dx, dy

        
        c = latitude_correction_magnitude(dx, dy)
        print c

        # print latitude_correction_magnitude(*euclidean_direction(cur_index, min_index))

        # print min_dist, min_dist * c *
        z[r][c] = min_dist

        raise


    trow_end = int(time.time())
    row_dur = trow_end - trow_start
    print "Row {0} ran in {1} seconds".format(r, row_dur)
    
    # raise


print x
print z



