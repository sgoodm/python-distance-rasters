import time
import numpy as np
from affine import Affine
from scipy.spatial import cKDTree
from .utils import export_raster, convert_index_to_coords, calc_haversine_distance


def build_distance_array(raster_array, affine=None, output=None, conditional=None):
    """build distance array from raster array

    Args
        raster_array (np array):
            array to use for distance calculations
        affine (Affine): [optional]
            affine transformation defining spatial raster data
        output (str): [optional, requires affine arg]
            path to export distance array as geotiff raster
        conditional (function): [optional]
            function which applies conditional to raster_array in order to
            define which elements distances are calculate to
            (default function finds distance to elements with a value of 1)

    Returns
        resulting distance array
    """
    if not isinstance(raster_array, np.ndarray):
        raise TypeError("Raster array must be a numpy array")

    if affine is not None and not isinstance(affine, Affine):
        raise TypeError("If provided, affine must be an instance of Affine class")

    if affine is None and output is not None:
        raise Exception("Affine is required for output")

    if affine is not None:
        pixel_size = affine[0]

    nrows, ncols = raster_array.shape

    def default_conditional(rarray):
        return rarray == 1

    if conditional is None:
        conditional = default_conditional

    elif not callable(conditional):
        raise Exception("Conditional must be function")


    # kd-tree instance
    # https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.spatial.cKDTree.html
    #
    # Alternatives (slower during testing):
    #   from sklearn.neighbors import KDTree, BallTree
    #   http://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KDTree.html
    #   http://scikit-learn.org/stable/modules/generated/sklearn.neighbors.BallTree.html
    #
    # As of SciPy v1.6.0, cKDTree is identical to KDTree. scipy>=1.6.0 is now a requirement
    t_start = time.time()
    k = KDTree(data=np.array(np.where(conditional(raster_array))).T, leafsize=64)
    print("Tree build time: {0} seconds".format(time.time() - t_start))

    print("Building distance array...")
    # output array for distance raster results
    z = np.empty(raster_array.shape, dtype=float)
    for r in range(nrows):

        for c in range(ncols):

            cur_index = (r, c)
            min_dist, min_index = k.query([cur_index])
            min_dist = min_dist[0]
            min_index = k.data[min_index[0]]

            if affine is not None:
                if cur_index[1] == min_index[1]:
                    # columns are same meaning nearest is either vertical or self.
                    # no correction needed, just convert to km
                    dd_min_dist = min_dist * pixel_size
                    km_min_dist = dd_min_dist * 111.321

                else:
                    km_min_dist = calc_haversine_distance(
                        convert_index_to_coords(cur_index, affine),
                        convert_index_to_coords(min_index, affine),
                    )

                val = km_min_dist * 1000

            else:
                val = min_dist

            z[r][c] = val



    print("Total run time: {0} seconds".format(round(time.time() - t_start, 2)))

    if output is not None:
        export_raster(z, affine, output)

    return z
