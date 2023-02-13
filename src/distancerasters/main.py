import time
import numpy as np
from affine import Affine
from scipy.spatial import KDTree
from .utils import export_raster, convert_index_to_coords, calc_haversine_distance


class DistanceRaster(object):

    def __init__(self, raster_array, affine=None, conditional=None, output_path=None):
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
        """
        if not isinstance(raster_array, np.ndarray):
            raise TypeError("Raster array must be a numpy array")

        if affine is not None and not isinstance(affine, Affine):
            raise TypeError("If provided, affine must be an instance of Affine class")

        if affine is None and output_path is not None:
            raise Exception("Affine is required for output")

        pixel_size = None
        if affine is not None:
            pixel_size = affine[0]

        if conditional is None:
            conditional = self.default_conditional

        elif not callable(conditional):
            raise Exception("Conditional must be function")


        self.conditional = conditional
        self.raster_array = raster_array
        self.pixel_size = pixel_size
        self.affine = affine

        self.tree = None
        self.dist_array = None

        self._build_tree()
        self._calculate_distance()

        if output_path is not None:
            self.output_raster(output_path)


    def default_conditional(self, rarray):
        return rarray == 1


    def _build_tree(self, tree_type='kdtree'):
        # kd-tree instance
        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.KDTree.html
        t_start = time.time()
        if tree_type == "kdtree":
            self.tree = KDTree(data=np.array(np.where(self.conditional(self.raster_array))).T, leafsize=64)
        print("Tree build time: {0} seconds".format(round(time.time() - t_start, 4)))


    def _calculate_distance(self):

        nrows, ncols = self.raster_array.shape
        self.dist_array = np.empty(self.raster_array.shape, dtype=float)

        t_start = time.time()

        for r in range(nrows):

            for c in range(ncols):

                cur_index = (r, c)
                min_dist, min_index = self.tree.query([cur_index])
                min_dist = min_dist[0]
                min_index = self.tree.data[min_index[0]]

                if self.affine is not None:
                    if cur_index[1] == min_index[1]:
                        # columns are same meaning nearest is either vertical or self.
                        # no correction needed, just convert to km
                        dd_min_dist = min_dist * self.pixel_size
                        km_min_dist = dd_min_dist * 111.321

                    else:
                        km_min_dist = calc_haversine_distance(
                            convert_index_to_coords(cur_index, self.affine),
                            convert_index_to_coords(min_index, self.affine),
                        )

                    val = km_min_dist * 1000

                else:
                    val = min_dist

                self.dist_array[r][c] = val

        print("Distance calc run time: {0} seconds".format(round(time.time() - t_start, 4)))


    def output_raster(self, output_path):
        export_raster(self.dist_array, self.affine, output_path)
