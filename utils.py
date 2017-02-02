

import math
import fiona
import rasterio
from rasterio import features
from affine import Affine
import numpy as np


def rasterize(path, pixel_size=None, output=None):
    """Rasterize features

    Args
        path (str): path to fiona compatible file containing features
        pixel_size (float): resolution at which to rasterize features
        output (str): (optional) output path for raster of rasterized features
    Returns
        array representing rasterized features
        affine of resoluting raster
        boundary of raster
    """


    if pixel_size is None:
        pixel_size = 0.01
    else:
        try:
            pixel_size = float(pixel_size)
        except:
            raise Exception("Invalid pixel size (could not be converted to float)")

    psi = 1 / pixel_size


    shp = fiona.open(path, "r")
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


    if output is not None:

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
            # 'nodata': 0,
            # 'compress': 'lzw'
        }

        raster_out = np.array([rv_array.astype(out_dtype)])

        # write geotif file
        with rasterio.open(output, "w", **meta) as dst:
            dst.write(raster_out)


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


    return rv_array, affine


def export_raster(raster, affine, path):

    out_dtype = 'float64'
    # affine takes upper left
    # (writing to asc directly used lower left)
    meta = {
        'count': 1,
        'crs': {'init': 'epsg:4326'},
        'dtype': out_dtype,
        'affine': affine,
        'driver': 'GTiff',
        'height': z.shape[0],
        'width': z.shape[1],
        'nodata': -1,
        # 'compress': 'lzw'
    }

    raster_out = np.array([z.astype(out_dtype)])

    # write geotif file
    with rasterio.open(path, "w", **meta) as dst:
        dst.write(raster_out)


def convert_index_to_coords(index, affine):
    """convert index values to coordinates

    used to converted x,y index of 2d matrix element
    (e.g., a raster) to coordinates (lon, lat) based
    on coordinates represented by top and left of
    matrix as well as pixel size represented by
    each element

    returns centroids of pixels for accurate distance
    calculations using results
    """
    r, c = index

    pixel_size = affine[0]
    xmin = affine[2]
    lon = xmin + pixel_size * (0.5 + c)

    ymax = affine[5]
    lat = ymax - pixel_size * (0.5 + r)

    return (lon, lat)


def calc_haversine_distance(p1, p2):
    """calculate haversine distance between two points

    # formula info
    # https://en.wikipedia.org/wiki/Haversine_formula
    # http://www.movable-type.co.uk/scripts/latlong.html

    Args
        p1: tuple of (longitude, latitude) format containing int or float values
        p2: tuple of (longitude, latitude) format containing int or float values
    Returns
        d (float): haversine distance between given points p1 and p2
    """
    lon1, lat1 = p1
    lon2, lat2 = p2
    # km
    radius = 6371.0
    # difference in rads
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = (math.sin(delta_lat/2)**2 + math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) * math.sin(delta_lon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    # km
    d = radius * c
    return d

