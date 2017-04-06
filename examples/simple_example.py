
import os
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import fiona
from distancerasters import build_distance_array, rasterize, export_raster


# -----------------------------------------------------------------------------

shp_path = "{0}/data/line_test.shp".format(base)
out_name = "line_test"

# shp_path = "data/line_test/big_line.shp"
# out_name = "big_line"

# -----------------------------------------------------------------------------

pixel_size = 0.01

rasterized_features_path = "{0}/data/{1}_binary.tif".format(base, out_name)

shp = fiona.open(shp_path, "r")
rv_array, affine = rasterize(shp, pixel_size=pixel_size, bounds=shp.bounds,
                             output=rasterized_features_path)

# export_raster(rv_array, affine, rasterized_features_path)


# print rv_array
print rv_array.shape
print affine

# -----------------------------------------------------------------------------

distance_raster_path = "{0}/data/{1}_distance.tif".format(base, out_name)

def raster_conditional(rarray):
    return (rarray == 1)

build_distance_array(rv_array, affine=affine,
                     output=distance_raster_path,
                     conditional=raster_conditional)


