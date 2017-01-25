

import math
import fiona
import rasterio
from rasterio import features
from affine import Affine

import numpy as np




def fake_rasterize():
    # x = np.random.randint(2, size=(int(180/10), int(360/10)))
    # x = np.random.randint(2, size=(10, 20))


    pixel_size = 0.1
    x = np.random.choice([0, 1], size=(int(180/pixel_size), int(360/pixel_size)), p=[.8, .2])



    x = np.array([
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

    return x




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
            'nodata': 0,
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


    return rv_array, affine, bnds



