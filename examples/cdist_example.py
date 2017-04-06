

import os
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from distancerasters import build_distance_array, rasterize, export_raster

from distancerasters import distance
from distancerasters.utils import convert_index_to_coords, calc_haversine_distance


import fiona
import numpy as np
import math



# -------------------------------------

shp_path = "{0}/data/line_test.shp".format(base)
out_name = "line_test"

# -------------------------------------

rasterized_feature_output_path = "{0}/data/{1}_binary.tif".format(base, out_name)
output_raster_path = "{0}/data/{1}_distance.tif".format(base, out_name)



# 0.1 is probably too coarse for quality
# 0.001 might be more than we need for quality
#   test with central america rivers @ 30s res
#   run time for rasterization was reasonable
#   distance processes may be too slow at this fine scale though
# testing with 0.01 for now
pixel_size = 0.01

shp = fiona.open(shp_path, "r")

rv_array, affine = rasterize(shp, pixel_size=pixel_size, bounds=shp.bounds,
                             output=rasterized_feature_output_path)
# rv_array = fake_rasterize()


# max distance in cells
# for actual distance: max_dist * pixel_size
max_dist = 100

nrows, ncols = rv_array.shape


# print rv_array
print rv_array.shape
print nrows * ncols

# raise

z = np.empty(rv_array.shape, dtype=float)

# -----------------------------------------------------------------------------

import time
t_start = time.time()

# row_dur = 0
# row_count = 0

t1 = 0
t1c = 0
t111 = 0
t111c = 0
t2 = 0
t2c = 0
t22 = 0
t22c = 0
t3 = 0
t3c = 0

for r in range(nrows):
# for r in range(1000, 1100):

    if r == 0 or r+1 % 50 == 0:
        trow_start = time.time()

    for c in range(ncols):
    # for c in range(1000, 1100):

        cur_index = (r, c)
        # print "Current index (r, c): {0}".format(cur_index)
        # print "Current coords (lon, lat): {0}".format(
            # convert_index_to_coords(cur_index, affine))

        t1s = time.time()

        rmin = r - max_dist if r >= max_dist else 0
        rmax = r + max_dist if r <= nrows - max_dist else nrows
        cmin = c - max_dist if c >= max_dist else 0
        cmax = c + max_dist if c <= ncols - max_dist else ncols

        sub_raster = rv_array[rmin:rmax, cmin:cmax]


        t1 += time.time() - t1s
        t1c += 1


        # print "\trmin: {0}, rmax: {1}, cmin: {2}, cmax: {3}, ".format(
        #     rmin, rmax, cmin, cmax)
        # print sub_raster


        t111s = time.time()

        line_indexes = np.array(np.nonzero(sub_raster)).T

        t111 += time.time() - t111s
        t111c += 1


        # print len(line_indexes)
        # print line_indexes
        if len(line_indexes) == 0:
            # print "\tOut of range"
            z[r][c] = -1
            continue


        t2s = time.time()

        # convert current index to sub index range
        sub_cur_index = (cur_index[0]-rmin, cur_index[1]-cmin)

        dist_list = distance.cdist([sub_cur_index], line_indexes)[0]
        min_dist = min(dist_list)

        t2 += time.time() - t2s
        t2c += 1



        t22s = time.time()

        dist_list_index = np.where(dist_list == min_dist)

        # # handle multiple min matches
        # for i in dist_list_index:
        #     print line_indexes[i]

        # just take first if there are multiple min matches
        sub_min_index = line_indexes[dist_list_index[0][0]]

        # convert min_index from sub_raster to
        # main raster index
        min_index = (sub_min_index[0] + rmin,
                     sub_min_index[1] + cmin)

        t22 += time.time() - t22s
        t22c += 1


        # print "\tsub_cur_index: {0}".format(sub_cur_index)
        # print "\tMin coords (lon, lat): {0}".format(
        #     convert_index_to_coords(min_index, affine))

        # print "\tsub_min_index: {0}".format(sub_min_index)
        # print dist_list
        # print "\tmin_dist: {0}".format(min_dist)
        # print dist_list_index
        # print "\tmin_index: {0}".format(min_index)


        t3s = time.time()

        if cur_index[1] == min_index[1]:

            # columns are different meaning nearest is
            # either vertical or self.
            # no correction needed,
            # just convert to meters

            dd_min_dist = min_dist * pixel_size
            m_min_dist = dd_min_dist * 111.321 * 10**3

            # print "\tdd_min_dist: {0}".format(dd_min_dist)
            # print "\tm_min_dist: {0}".format(m_min_dist)

            val = m_min_dist


        else:

            val = calc_haversine_distance(
                convert_index_to_coords(cur_index, affine),
                convert_index_to_coords(min_index, affine)
            ) * 1000


        t3 += time.time() - t3s
        t3c += 1

        # print "\tval: {0}".format(val)
        z[r][c] = val

        # raise

    if r+1 % 50 == 0:
        print "Row {0}-{1}/{2} ran in {3} seconds".format(r+1-50, r+1, nrows, time.time() - trow_start)

    # row_dur += time.time() - trow_start
    # row_count += 1

    # if r == 200:
    #     print "Run time: {0} seconds for {1} rows ({2}s avg)".format(row_dur, row_count, row_dur/row_count)

    #     print "t1 total: {0}, count: {1}, avg: {2}".format(t1, t1c, t1/t1c)
    #     print "t11 total: {0}, count: {1}, avg: {2}".format(t11, t11c, t11/t11c)
    #     print "t111 total: {0}, count: {1}, avg: {2}".format(t111, t111c, t111/t111c)

    #     print "t2 total: {0}, count: {1}, avg: {2}".format(t2, t2c, t2/t2c)
    #     print "t22 total: {0}, count: {1}, avg: {2}".format(t22, t22c, t22/t22c)
    #     print "t3 total: {0}, count: {1}, avg: {2}".format(t3, t3c, t3/t3c)

    #     raise


# print rv_array
# print z

print rv_array.shape
print nrows * ncols

print "t1 total: {0}, count: {1}, avg: {2}".format(t1, t1c, t1/t1c)
print "t111 total: {0}, count: {1}, avg: {2}".format(t111, t111c, t111/t111c)

print "t2 total: {0}, count: {1}, avg: {2}".format(t2, t2c, t2/t2c)
print "t22 total: {0}, count: {1}, avg: {2}".format(t22, t22c, t22/t22c)
print "t3 total: {0}, count: {1}, avg: {2}".format(t3, t3c, t3/t3c)

dur = time.time() - t_start
print "Run time: {0} seconds".format(round(dur, 2))



export_raster(z, affine, output_raster_path)
