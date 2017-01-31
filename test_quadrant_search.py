

import numpy as np

import distance


# pixel_size = 0.1
# rv_array = np.random.choice([0, 1], size=(int(180/pixel_size), int(360/pixel_size)),
#                      p=[.8, .2])


rv_array = np.array([
    [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
])

nrows, ncols = rv_array.shape


print rv_array
print rv_array.shape

# if subset resulting from quadrant reduction
# results in either dimension falling below this
# value, do not process any additional levels
# (i.e., it is small enough that further reduction
# will not matter)
min_sub_raster_size = 4

# how many times (maximum) the grid will be subset into quadrants
# before running distance calculations on resulting sub grid
nlevels = 2

active_center = (int(round(nrows * 0.5)), int(round(ncols * 0.5)))

for r in range(nrows):

    for c in range(ncols):

        cur_index = (r, c)
        print "Current index (r, c): {0}".format(cur_index)


        # use nlevels + 2 since range is starting at 1
        # and we need to go one extra time to build the subgrid
        # for the final level that runs
        for level in range(1, nlevels+2):

            print "\n\tPreparing Level {0}".format(level-1)
            print "\t\tActive Center (r, c): {0}".format(active_center)

            # define bounds of subset for current level
            # (based on level and active center)
            rmin = int(np.floor(active_center[0] - nrows / (2 * level)))
            rmax = int(np.ceil(active_center[0] + nrows / (2 * level)))
            cmin = int(np.floor(active_center[1] - ncols / (2 * level)))
            cmax = int(np.ceil(active_center[1] + ncols / (2 * level)))

            rmin = rmin if rmin >= 0 else 0
            rmax = rmax if rmax <= nrows else nrows
            cmin = cmin if cmin >= 0 else 0
            cmax = cmax if cmax <= ncols else ncols

            print "\t\trmin: {0}, rmax: {1}".format(rmin, rmax)
            print "\t\tcmin: {0}, cmax: {1}".format(cmin, cmax)


            # check if resulting subset is less than minimum
            # allowable size for subgrid
            min_size = (cmax-cmin < min_sub_raster_size
                        or rmax-rmin < min_sub_raster_size)


            if min_size or level > nlevels:
                # if grid is min size or hit max number of levels
                break

            else:
                # search quadrants centroids to define the next level
                print "\n\t\tRunning Level {0} Search".format(level)

                # generate set of 4 center points for current level quadrant
                quad_points = [
                    (rmin + (rmax-rmin) * 0.25, cmin + (cmax-cmin) * 0.25),
                    (rmin + (rmax-rmin) * 0.25, cmin + (cmax-cmin) * 0.75),
                    (rmin + (rmax-rmin) * 0.75, cmin + (cmax-cmin) * 0.25),
                    (rmin + (rmax-rmin) * 0.75, cmin + (cmax-cmin) * 0.75)
                ]


                dist_list = distance.cdist([cur_index], quad_points)[0]
                min_dist = min(dist_list)
                dist_list_index = np.where(dist_list == min_dist)[0][0]

                active_center = quad_points[dist_list_index]

                print "\t\tquad_points: {0}".format(quad_points)
                print "\t\tdist_list: {0}".format(dist_list)
                print "\t\tmin_dist: {0}".format(min_dist)
                print "\t\tdist_list_index: {0}".format(dist_list_index)

                print "\t\tactive_center: {0}".format(active_center)



        # ---------------------------------------------------------------------
        # run normal dist stuff for sub_raster

        sub_raster = rv_array[rmin:rmax, cmin:cmax]
        print sub_raster
        # ...


        raise
