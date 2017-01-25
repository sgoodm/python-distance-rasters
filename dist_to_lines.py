

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



