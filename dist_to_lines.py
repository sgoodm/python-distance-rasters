

# from scipy import spatial
# from scipy.spatial import KDTree as kdt

import numpy as np
import math

# from scipy import spatial
# from scipy.spatial import distance
import distance

from corrections import (euclidean_distance, euclidean_direction,
                         latitude_correction_magnitude, index_to_coords,
                         get_latitude_scale, calc_haversine_distance)

from rasterize import rasterize, fake_rasterize


# shp_path = "line_test/line_test.shp"
shp_path = "ca_riv_30s/ca_riv_30s.shp"

# 0.1 is probably too coarse for quality
# 0.001 might be more than we need for quality
#   test with central america rivers @ 30s res
#   run time for rasterization was reasonable
#   distance processes may be too slow at this fine scale though
# testing with 0.01 for now
pixel_size = 0.01

output_raster_path = "line_test_raster.tif"

# rv_array, affine, bnds = rasterize(path=shp_path, pixel_size=0.01, output=output_raster_path)
rv_array = fake_rasterize()


# max distance in cells
# for actual distance: max_dist * pixel_size
max_dist = 100

nrows, ncols = rv_array.shape



# print rv_array
print rv_array.shape
print nrows * ncols



z = np.empty(rv_array.shape, dtype=float)



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
        # print rleft, rright, cleft, cright

        x1 = rv_array[rleft:rright, cleft:cright]
        print x1

        # actual_indexes =

        y = np.ma.masked_array(x1, mask=(x1==0))
        # print y

        line_prep = np.ma.nonzero(y)
        line_indexes = zip(line_prep[0], line_prep[1])
        print len(line_indexes)
        print line_indexes

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

        if dx != 0 and dy != 0:
            theta = np.tan(dy/dx)
            delta_dy = np.sin(theta) * min_dist / 2
            haversine_index = cur_index[0] + delta_dy # does sign of delta_dy account for direction (N vs S)

            # haversine_lat = convert_index_to_lat(haversine_index)
            # h = get_latitude_scale(haversine_lat) # haversine scale

        c = latitude_correction_magnitude(dx, dy)
        # print c

        # print latitude_correction_magnitude(*euclidean_direction(cur_index, min_index))

        # print min_dist, min_dist * (c * h)
        z[r][c] = min_dist # * (c * h)

        # raise


    trow_end = int(time.time())
    row_dur = trow_end - trow_start
    print "Row {0} ran in {1} seconds".format(r, row_dur)

    if r == 5:
        raise


print rv_array
print z



