import time

import numpy as np
from affine import Affine

from distancerasters._distancerasters import calculate_distances
from .utils import export_raster


class DistanceRaster(object):

    def __init__(self, raster_array, affine=None, conditional=None, output_path=None, progress_bar=False):
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

        if conditional is None:
            conditional = self.default_conditional

        elif not callable(conditional):
            raise Exception("Conditional must be function")

        self.conditional = conditional
        self.raster_array = raster_array
        self.affine = affine

        self.dist_array = None

        self._calculate_distance()

        if output_path is not None:
            self.output_raster(output_path)


    def default_conditional(self, rarray):
        return rarray == 1


    def _calculate_distance(self):
        t_start = time.time()
        mask = self.conditional(self.raster_array)
        indices = np.array(np.where(mask)).T.astype(np.float64)
        print("Tree build time: {} seconds".format(round(time.time() - t_start, 4)))

        nrows, ncols = self.raster_array.shape

        affine_params = None
        if self.affine is not None:
            affine_params = (float(self.affine[0]), float(self.affine[2]), float(self.affine[5]))

        t_start = time.time()
        self.dist_array = calculate_distances(indices, nrows, ncols, affine_params)
        print("Distance calc run time: {} seconds".format(round(time.time() - t_start, 4)))


    def output_raster(self, output_path):
        export_raster(self.dist_array, self.affine, output_path)
