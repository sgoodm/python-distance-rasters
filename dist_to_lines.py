

# from scipy import spatial
# from scipy.spatial import KDTree as kdt

import numpy as np
import math

import rasterio

# from scipy import spatial
# from scipy.spatial import distance
import distance

from corrections import (euclidean_distance, euclidean_direction,
                         latitude_correction_magnitude,
                         convert_index_to_coords, convert_index_to_lat,
                         get_latitude_scale, calc_haversine_distance)

from rasterize import rasterize, fake_rasterize



shp_path = "line_test/line_test.shp"
rasterized_feature_output_path = "line_test_raster.tif"
output_raster_path = "line_test_distance_raster.tif"


shp_path = "ca_riv_30s/ca_riv_30s.shp"
rasterized_feature_output_path = "ca_riv_30s_raster.tif"
output_raster_path = "ca_riv_30s_distance_raster.tif"



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

z = np.empty(rv_array.shape, dtype=float)

# -----------------------------------------------------------------------------

import time
t_start = int(time.time())

for r in range(nrows):
    trow_start = int(time.time())
    for c in range(ncols):

        cur_index = (r, c)
        print "Current index (r, c): {0}".format(cur_index)
        print "Current coords (lon, lat): {0}".format(
            convert_index_to_coords(cur_index, affine))

        rmin = r - max_dist if r >= max_dist else 0
        rmax = r + max_dist if r <= nrows - max_dist else nrows
        cmin = c - max_dist if c >= max_dist else 0
        cmax = c + max_dist if c <= ncols - max_dist else ncols
        print "\trmin: {0}, rmax: {1}, cmin: {2}, cmax: {3}, ".format(
            rmin, rmax, cmin, cmax)

        sub_raster = rv_array[rmin:rmax, cmin:cmax]
        # print sub_raster

        # actual_indexes =

        y = np.ma.masked_array(sub_raster, mask=(sub_raster==0))
        # print y

        line_prep = np.ma.nonzero(y)
        line_indexes = zip(line_prep[0], line_prep[1])
        # print len(line_indexes)
        # print line_indexes

        if len(line_indexes) == 0:
            print "\tOut of range"
            z[r][c] = -1
            continue

        # from timeit import timeit
        # print timeit(lambda: [euclidean_distance(cur_index, tmp_index) for tmp_index in line_indexes], number=10000)
        # print timeit(lambda: distance.cdist([cur_index], line_indexes, 'euclidean')[0], number=10000)
        # raise

        # convert current index to sub index range
        sub_cur_index = (cur_index[0]-rmin, cur_index[1]-cmin)
        print "\tsub_cur_index: {0}".format(sub_cur_index)

        # dist_list = [euclidean_distance(cur_index, tmp_index) for tmp_index in line_indexes]
        dist_list = distance.cdist([sub_cur_index], line_indexes, 'euclidean')[0]
        min_dist = min(dist_list)
        dist_list_index = np.where(dist_list == min_dist)
        sub_min_index = line_indexes[dist_list_index[0][0]]

        # convert min_index from sub_raster to
        # main raster index
        min_index = (sub_min_index[0] + rmin,
                     sub_min_index[1] + cmin)

        print "\tMin coords (lon, lat): {0}".format(
            convert_index_to_coords(min_index, affine))

        # for i in dist_list_index:
            # print line_indexes[i]

        print "\tsub_min_index: {0}".format(sub_min_index)
        # print dist_list
        print "\tmin_dist: {0}".format(min_dist)
        # print dist_list_index
        print "\tmin_index: {0}".format(min_index)


        # values of change in x and y
        # between current and nearest
        dx, dy = euclidean_direction(cur_index, min_index)

        # negate dy value
        # due to rows increase downward, opposite of latitude
        dy = dy * -1

        print "\tdx: {0}, dy: {1}".format(dx, dy)

        dd_min_dist = min_dist * pixel_size
        print "\tdd_min_dist: {0}".format(dd_min_dist)

        m_min_dist = dd_min_dist * 111.321 * 10**3
        print "\tm_min_dist: {0}".format(m_min_dist)



        if dx == 0 and dy == 0:
            # nearest is self
            val = 0

        elif dx == 0:
            # nearest is vertical
            # no correction needed
            val = m_min_dist

        elif dy == 0:
            # nearest is horizontal
            # pure latitude correction
            lat = convert_index_to_lat(cur_index[0], affine)
            h = get_latitude_scale(lat)
            val = m_min_dist * h

        else:
            # latitude correction scaled based
            # on direction of nearest
            theta = np.tan(float(dy) / float(dx))
            delta_dy = np.sin(theta) * (min_dist / 2)

            # subtract `delta_dy` because we need to negate
            # the original negation of `dy`
            new_row_index = int(round(cur_index[0] - delta_dy))

            print "\ttheta: {0}".format(theta)
            print "\tdelta_dy: {0}".format(delta_dy)
            print "\tnew_row_index: {0}".format(new_row_index)

            lat = convert_index_to_lat(new_row_index, affine)
            h = get_latitude_scale(lat)
            m = latitude_correction_magnitude(dx, dy)

            print "\tlat: {0}".format(lat)
            print "\tcorrection factor (h): {0}".format(h)
            print "\tcorrection magnitude (m): {0}".format(m)

            val = m_min_dist * (h * m) + m_min_dist * (1 - m)


        print "\tval: {0}".format(val)
        z[r][c] = val

        # raise


    trow_end = int(time.time())
    row_dur = trow_end - trow_start
    print "Row {0} ran in {1} seconds".format(r, row_dur)

    # if r == 20:
    #     t_end = int(time.time())
    #     dur = t_end - t_start
    #     print "Run time: {0} seconds".format(dur)
    #     raise


# print rv_array
# print z


t_end = int(time.time())
dur = t_end - t_start
print "Run time: {0} seconds".format(dur)


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
