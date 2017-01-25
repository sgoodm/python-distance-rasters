

import math
import fiona
import rasterio
from rasterio import features
from affine import Affine

import numpy as np

# 0.1 is probably too coarse for quality
# 0.001 might be more than we need for quality
#   test with central america rivers @ 30s res
#   run time for rasterization was reasonable
#   distance processes may be too slow at this fine scale though
# testing with 0.01 for now
pixel_size = 0.01
psi = 1 / pixel_size

# shp_path = "line_test/line_test.shp"
shp_path = "ca_riv_30s/ca_riv_30s.shp"

shp = fiona.open(shp_path, "r")
feats = [(feat['geometry'], 1) for feat in shp]

bnds = shp.bounds
xmin, ymin, xmax, ymax = bnds

xmin = math.floor(xmin * psi) / psi
ymin = math.floor(ymin * psi) / psi

xmax = math.ceil(xmax * psi) / psi + pixel_size
ymax = math.ceil(ymax * psi) / psi + pixel_size

shape = (int((ymax-ymin)*psi), int((xmax-xmin)*psi))

affine = Affine(pixel_size, 0, xmin,
                0, -pixel_size, ymax)




rv_array = features.rasterize(
    feats,
    out_shape=shape,
    transform=affine,
    fill=0,
    all_touched=True)



out_dtype = 'uint8'
# affine takes upper left
# (writing to asc directly used lower left)
meta = {
    'count': 1,
    'crs': {'init': 'epsg:4326'},
    'dtype': out_dtype,
    'affine': affine,
    'driver': 'GTiff',
    'height': shape[0],
    'width': shape[1],
    'nodata': 0,
    # 'compress': 'lzw'
}

raster_out = np.array([rv_array.astype(out_dtype)])


# ###
# print rv_array

# print bnds
# print xmin, ymin, xmax, ymax

# print shape
# print affine
# print rv_array.shape

# print meta
# print raster_out.shape
# ###


# write geotif file
with rasterio.open("line_test_raster.tif", "w", **meta) as dst:
    dst.write(raster_out)








# latitude_scale = [
#     get_latitude_scale(fsrc_affine[5] - fsrc_affine[0] * (0.5 + i))
#     for i in range(fsrc_shape[0])
# ]

# feature_stats['mean'] = float(
#     np.sum((masked.T * latitude_scale).T) /
#     np.sum(latitude_scale * (masked.shape[1] - np.sum(masked.mask, axis=1))))


