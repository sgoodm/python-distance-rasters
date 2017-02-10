
import os
import errno
import math
from warnings import warn
import fiona
import rasterio
from rasterio import features
from affine import Affine
import numpy as np


def rasterize(path, pixel_size=None, affine=None, shape=None, output=None):
    """Rasterize features

    Can choose to provide either pixel_size or both affine and shape

    Providing output path is optional. Only needed if you want to save
    rasterized feature(s) to a GeoTiff

    rasterio features rasterization function:
    https://mapbox.github.io/rasterio/topics/features.html
    https://mapbox.github.io/rasterio/_modules/rasterio/features.html

    Args
        path (str): path to fiona compatible file containing features
        pixel_size (float): resolution at which to rasterize features
        affine (Affine): affine transformation used for rasterization
        shp (tuple): shape for rasterization which corresponds with affine
        output (str): (optional) output path for raster of rasterized features

    Returns
        array representing rasterized features
        affine of resoluting raster
    """
    shp = fiona.open(path, "r")

    if (affine is not None and isinstance(affine, Affine)
        and shape is not None and isinstance(shape, tuple)
        and len(shape) == 2):

        if pixel_size is not None and pixel_size != affine[0]:
            warn('Ignoring pixel size provided due to valid affine and shape input.')

        # TODO:
        # does affine / shape need to be adjusted to match rounding
        # done when only pixel_size is provided?
        #   should assume if affine is output from an intial call to
        #   this function that the affine is already adjusted/clean

    elif pixel_size is not None:
        try:
            pixel_size = float(pixel_size)
        except:
            raise Exception("Invalid pixel size (could not be converted to float)")

        psi = 1 / pixel_size

        bnds = shp.bounds
        xmin, ymin, xmax, ymax = bnds

        xmin = math.floor(xmin * psi) / psi
        ymin = math.floor(ymin * psi) / psi

        xmax = math.ceil(xmax * psi) / psi + pixel_size
        ymax = math.ceil(ymax * psi) / psi + pixel_size

        shape = (int((ymax-ymin)*psi), int((xmax-xmin)*psi))

        affine = Affine(pixel_size, 0, xmin,
                        0, -pixel_size, ymax)

    else:
        raise Exception('Must provide either pixel size or affine and shape')

    # TODO:
    # could use field arg + dict lookup for non-binary rasters
    rvalue = 1
    feats = [(feat['geometry'], rvalue) for feat in shp]

    rv_array = features.rasterize(
        feats,
        out_shape=shape,
        transform=affine,
        fill=0,
        default_value=1,
        all_touched=True,
        dtype=None
    )

    if output is not None:
        export_raster(rv_array, affine, output)

    # print rv_array

    # print xmin, ymin, xmax, ymax

    # print shape
    # print affine
    # print rv_array.shape

    return rv_array, affine


def make_dir(path):
    """Make directory.

    Args:
        path (str): absolute path for directory

    Raise error if error other than directory exists occurs.
    """
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def export_raster(raster, affine, path):
    """Export raster array to geotiff
    """
    out_dtype = 'float64'
    # affine takes upper left
    # (writing to asc directly used lower left)
    meta = {
        'count': 1,
        'crs': {'init': 'epsg:4326'},
        'dtype': out_dtype,
        'affine': affine,
        'driver': 'GTiff',
        'height': raster.shape[0],
        'width': raster.shape[1],
        # 'nodata': -1,
        # 'compress': 'lzw'
    }

    raster_out = np.array([raster.astype(out_dtype)])

    make_dir(os.path.dirname(path))

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

    same as using affine to transform col,row to x,y
    but this takes significantly less time
        e.g., (lon, lat) = (col,row) * affine
    this also adjusts by half pixel size value to
    use centroid of cells (not a big deal, but can
    change haversine distances slightly)

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

