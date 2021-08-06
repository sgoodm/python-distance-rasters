"""
Warning: the data to run this file is not available locally

This is intended only to show how the rasterization can be
used to create more complex dataset than simply rasterizing
a single feature layer
"""

import numpy as np
from affine import Affine
from distancerasters as dr


# paths to multiple vector datasets
oceans_path = "oceans.geojson"
lakes_path = "lakes.geojson"
rivers_path = "rivers.geojson"

# define resolution
pixel_size = 0.01

# define shape and affine based on pixel size and bounds for desired area
#    because we are rasterizing multiple layers with different bounding boxes,
#    we likely want to specify a custom bounding box

xmin = -180
xmax = 180
ymin = -90
ymax = 90

affine = Affine(pixel_size, 0, xmin,
                0, -pixel_size, ymax)

shape = (int((ymax-ymin)/pixel_size), int((xmax-xmin)/pixel_size))


# rasterize all layers using the common bounding box so that we can combine
# resulting rasterized arrays later
oceans, _ = dr.rasterize(oceans_path, affine=affine, shape=shape)
lakes, _ = dr.rasterize(lakes_path, affine=affine, shape=shape)
rivers, _ = dr.rasterize(rivers_path, affine=affine, shape=shape)

# combine rasterized arrays
water = oceans + lakes + rivers


# generate distance raster

def raster_conditional(rarray):
    return (rarray == 1)

distance_output_raster_path = "water_distance.tif"

dist = dr.DistanceRaster(water, affine=affine,
                         output_path=distance_output_raster_path,
                         conditional=raster_conditional)


