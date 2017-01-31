

import numpy as np
import math

import rasterio

from scipy.spatial import cKDTree as kdt

import distance

from corrections import convert_index_to_coords, calc_haversine_distance

from rasterize import rasterize


# -------------------------------------

# shp_path = "data/line_test/line_test.shp"
# out_name = "line_test"

# shp_path = "data/line_test/big_line.shp"
# out_name = "big_line"

# shp_path = "data/ca_riv_30s/ca_riv_30s.shp"
# out_name = "ca_riv_30s_sub1"

shp_path = "data/ca_riv_15s/ca_riv_15s.shp"
out_name = "ca_riv_15s_1klimit"

# -------------------------------------

rasterized_feature_output_path = "data/{0}_raster.tif".format(out_name)
output_raster_path = "data/{0}_distance_raster.tif".format(out_name)



# 0.1 is probably too coarse for quality
# 0.001 might be more than we need for quality
#   test with central america rivers @ 30s res
#   run time for rasterization was reasonable
#   distance processes may be too slow at this fine scale though
# testing with 0.01 for now
pixel_size = 0.01


rv_array, affine, bnds = rasterize(path=shp_path, pixel_size=pixel_size,
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

# https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.spatial.cKDTree.html
k = kdt(
    data=np.array(np.where(rv_array == 1)).T
)


z = np.empty(rv_array.shape, dtype=float)

# -----------------------------------------------------------------------------

import time
t_start = time.time()

# row_dur = 0
# row_count = 0

t1 = 0
t1c = 0

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

        min_dist, min_index = k.query([cur_index], n_jobs=-1)

        min_dist = min_dist[0]
        min_index = k.data[min_index[0]]

        t1 += time.time() - t1s
        t1c += 1




        # print "\tmin_dist: {0}".format(min_dist)
        # print "\tmin_index: {0}".format(min_index)

        # print "\tMin coords (lon, lat): {0}".format(
        #     convert_index_to_coords(min_index, affine))



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
    #     print "t3 total: {0}, count: {1}, avg: {2}".format(t3, t3c, t3/t3c)

    #     raise


# print rv_array
# print z

print rv_array.shape
print nrows * ncols

print "t1 total: {0}, count: {1}, avg: {2}".format(t1, t1c, t1/t1c)
print "t3 total: {0}, count: {1}, avg: {2}".format(t3, t3c, t3/t3c)

dur = time.time() - t_start
print "Run time: {0} seconds".format(round(dur, 2))


# raise


out_dtype = 'float64'
# affine takes upper left
# (writing to asc directly used lower left)
meta = {
    'count': 1,
    'crs': {'init': 'epsg:4326'},
    'dtype': out_dtype,
    'affine': affine,
    'driver': 'GTiff',
    'height': nrows,
    'width': ncols,
    'nodata': -1,
    # 'compress': 'lzw'
}

raster_out = np.array([z.astype(out_dtype)])

# write geotif file
with rasterio.open(output_raster_path, "w", **meta) as dst:
    dst.write(raster_out)
