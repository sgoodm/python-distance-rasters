

import numpy as np
import rasterio

from scipy.spatial import cKDTree

from rasterize import rasterize
from corrections import convert_index_to_coords, calc_haversine_distance


# -------------------------------------

# shp_path = "data/line_test/line_test.shp"
# out_name = "line_test"

# shp_path = "data/line_test/big_line.shp"
# out_name = "big_line"

shp_path = "data/ca_riv_15s/ca_riv_15s.shp"
out_name = "ca_riv_15s"

# -------------------------------------

rasterized_feature_output_path = "data/{0}_raster.tif".format(out_name)
output_raster_path = "data/{0}_distance_raster.tif".format(out_name)



# 0.1 is probably too coarse for quality
# 0.001 might be more than we need for quality
#   test with central america rivers @ 15s res
#   run time for rasterization was reasonable
#   distance processes may be too slow at this fine scale though
# testing with 0.01 for now
pixel_size = 0.01


rv_array, affine, bnds = rasterize(path=shp_path, pixel_size=pixel_size,
                                   output=rasterized_feature_output_path)

nrows, ncols = rv_array.shape

# print rv_array
print rv_array.shape
print nrows * ncols

# raise


# array for distance raster results
z = np.empty(rv_array.shape, dtype=float)


# -----------------------------------------------------------------------------


import time
t_start = time.time()


# kd-tree instance
# https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.spatial.cKDTree.html
#
# Alternatives (slower during testing):
#   from sklearn.neighbors import KDTree, BallTree
#   http://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KDTree.html
#   http://scikit-learn.org/stable/modules/generated/sklearn.neighbors.BallTree.html

k = cKDTree(
    data=np.array(np.where(rv_array == 1)).T,
    leafsize=64
)

print "Tree build time: {0} seconds".format(time.time() - t_start)


# -----------------------------------------------------------------------------



t1, t1c = 0, 0
t2, t2c = 0, 0

for r in range(nrows):

    for c in range(ncols):

        cur_index = (r, c)
        # print "Current index (r, c): {0}".format(cur_index)
        # print "Current coords (lon, lat): {0}".format(
            # convert_index_to_coords(cur_index, affine))


        # t1s = time.time()

        min_dist, min_index = k.query([cur_index])

        min_dist = min_dist[0]
        min_index = k.data[min_index[0]]

        # t1 += time.time() - t1s
        # t1c += 1


        # print "\tmin_dist: {0}".format(min_dist)
        # print "\tmin_index: {0}".format(min_index)

        # print "\tMin coords (lon, lat): {0}".format(
        #     convert_index_to_coords(min_index, affine))


        # t2s = time.time()

        if cur_index[1] == min_index[1]:

            # columns are same meaning nearest is either vertical or self.
            # no correction needed, just convert to km

            dd_min_dist = min_dist * pixel_size
            km_min_dist = dd_min_dist * 111.321

        else:

            km_min_dist = calc_haversine_distance(
                convert_index_to_coords(cur_index, affine),
                convert_index_to_coords(min_index, affine)
            )


        # t2 += time.time() - t2s
        # t2c += 1

        z[r][c] = km_min_dist * 1000

        # print "\tMin dist (m): {0}".format(km_min_dist * 1000)
        # raise



# print rv_array
# print z
# print rv_array.shape
# print nrows * ncols

# print "t1 total: {0}, count: {1}, avg: {2}".format(t1, t1c, t1/t1c)
# print "t2 total: {0}, count: {1}, avg: {2}".format(t2, t2c, t2/t2c)

dur = time.time() - t_start
print "Distance run time: {0} seconds".format(round(dur, 2))


# -----------------------------------------------------------------------------

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
