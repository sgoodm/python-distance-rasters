import os
import math
import fiona
from shapely.geometry import mapping, LineString
import pytest
from distancerasters.utils import rasterize, export_raster, calc_haversine_distance

@pytest.fixture
def example_shapefile():
    # Some of this code from https://gis.stackexchange.com/a/52708

    # Path to write shapefile to
    dest_path = "test_shapefile.shp"

    # Example WKT-style LINESTRING as a Shapely object
    # Geometry from https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry
    line = LineString([(3, 1), (1, 3), (4, 4)])

    # Define a linestring feature geometry with one attribute
    schema = {
        'geometry': 'LineString',
        'properties': {'id': 'int'},
    }

    # Write a new Shapefile
    with fiona.open(dest_path, 'w', 'ESRI Shapefile', schema) as c:
        c.write({
            'geometry': mapping(line),
            'properties': {'id': 123},
        })

    return dest_path

@pytest.fixture
def example_raster(example_shapefile):
    shp = fiona.open(example_shapefile, "r")
    rv_array, affine = rasterize(shp, pixel_size=1, bounds=shp.bounds)
    return rv_array

@pytest.fixture
def example_affine(example_shapefile):
    shp = fiona.open(example_shapefile, "r")
    rv_array, affine = rasterize(shp, pixel_size=1, bounds=shp.bounds)
    return affine

@pytest.fixture
def example_path():
    return "lorem/ipsum/dolor/amet"

def test_rasterize(example_shapefile):
    shp = fiona.open(example_shapefile, "r")
    rv_array, affine = rasterize(shp, pixel_size=0.5, bounds=shp.bounds)
    expected_output = [[0,0,0,1,1,1],
                       [1,1,1,1,0,0],
                       [1,0,0,0,0,0],
                       [0,1,0,0,0,0],
                       [0,0,1,0,0,0],
                       [0,0,0,1,0,0]]
    assert (rv_array == expected_output).all

def test_bad_rasterize():
    assert 1

def test_export_raster():
    
    # open it again and see if it has the same Affine, height/width/shape, and the same data that we wrote to it
    assert 1

def test_bad_export_raster(example_raster, example_affine, example_path):

    # TODO: pass bad raster to export_raster

    # TODO: pass bad path to export_raster

    with pytest.raises(TypeError):
        export_raster(example_raster, example_affine, example_path, 42)

    """
    with pytest.raises(ValueError):
        export_raster(example_raster, example_affine, example_path, "float42")
    """

    # TODO: pass bad nodata to export_raster


# TODO: def test_convert_index_to_coords(index, affine):


def test_calc_haversine_distance():
    # Test distance that should be zero
    assert calc_haversine_distance((0, -180), (180, 0)) == 0

    # More complex test calculation that requires every aspect of the function
    a = math.cos(math.pi / 2) * math.sqrt(2) / 8 + math.sin(math.pi / 8) ** 2
    expected_output = math.atan2(math.sqrt(a), math.sqrt(1 - a)) * 12742
    assert calc_haversine_distance((math.pi, -90), (4 * (math.pi / 3), -45)) == expected_output

    # Make sure output is float
    assert isinstance(calc_haversine_distance((0, 0), (0, 0)), float)
