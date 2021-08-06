import os
import math
from affine import Affine
import numpy as np
from shapely.geometry import shape
import rasterio
import geopandas as gpd
import pytest
from distancerasters.utils import (
    get_affine_and_shape,
    rasterize,
    export_raster,
    convert_index_to_coords,
    calc_haversine_distance,
)


@pytest.fixture
def example_shape():
    # geometry from (1/10 scale):
    # https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry
    return shape({"type": "LineString", "coordinates": [(3, 1), (1, 3), (4, 4)]})


@pytest.fixture
def example_feature():
    # geometry from (1/10 scale):
    # https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry
    return {"type": "Feature", "geometry": shape({"type": "LineString", "coordinates": [(3, 1), (1, 3), (4, 4)]}), "properties": {"id": 1}}




@pytest.fixture
def example_raster():
    # returns a raster that represents a rasterized example_shape
    # with pixel_size = 0.5
    return np.array(
        [
            [0, 0, 0, 1, 1, 1],
            [1, 1, 1, 1, 0, 0],
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
        ]
    )


@pytest.fixture
def example_affine():
    return Affine(1.5, 1.0, 0.0, 1.0, 1.5, 1.0)


@pytest.fixture
def example_path():
    path = "tests/testdata/lorem/ipsum/dolor/amet"
    # remove any file at example_path that may have been created in previous tests
    if os.path.isfile(path):
        os.remove(path)
    return path


def test_get_affine_and_shape():
    output_affine, output_shape = get_affine_and_shape((1, 4, 3, 6), 0.5)
    assert output_affine == Affine(0.5, 0.0, 1.0, 0.0, -0.5, 6.0)
    assert output_shape == (4, 4)


def test_bad_get_affine_and_shape():
    with pytest.raises(TypeError):
        get_affine_and_shape((0, 0, 0, 0), "string")


def test_rasterize(example_shape, example_raster, example_path):

    # pass shapely shape geometry to rasterize
    output_raster = rasterize(
        example_shape, pixel_size=0.5, bounds=example_shape.bounds
    )[0]
    assert (output_raster == example_raster).all



def test_rasterize_output(example_shape, example_raster, example_path):

    # same as above, with output path
    output_raster = rasterize(
        example_shape, pixel_size=0.5, bounds=example_shape.bounds, output=example_path
    )[0]
    # open raster written to example_path and make sure the data matches
    with rasterio.open(example_path) as src:
        assert (src.read() == example_raster).all


def test_rasterize_with_attribute(example_shape, example_raster):

    geodataframe = gpd.GeoDataFrame([{"id": 0, "geometry": example_shape, "value": 2}])

    # pass geodataframe to rasterize
    output_raster = rasterize(
        geodataframe, pixel_size=0.5, bounds=geodataframe.total_bounds, attribute="value"
    )[0]
    assert (output_raster == example_raster * 2).all()


def test_geodataframe_rasterize(example_shape, example_raster):

    geodataframe = gpd.GeoDataFrame([{"id": 0, "geometry": example_shape}])

    # pass geodataframe to rasterize
    output_raster = rasterize(
        geodataframe, pixel_size=0.5, bounds=geodataframe.total_bounds
    )[0]
    assert (output_raster == example_raster).all()


def test_iterable_rasterize(example_feature, example_raster):

    bounds = shape(example_feature["geometry"]).bounds
    example_iterable = [example_feature]

    # pass iterable of geometry to rasterize
    output_raster = rasterize(
        example_iterable, pixel_size=0.5, bounds=bounds
    )[0]
    assert (output_raster == example_raster).all


def test_bad_rasterize(example_shape, example_affine):

    # warns about ignoring pixel_size because valid affine and shape were passed
    with pytest.warns(UserWarning):
        rasterize(example_shape, pixel_size=0.5, shape=(2, 4), affine=example_affine)[0]

    # warns about ignoring bounds because valid affine and shape were passed
    with pytest.warns(UserWarning):
        rasterize(
            example_shape,
            pixel_size=1.5,
            shape=(2, 4),
            bounds=(0, 1, 2, 3),
            affine=example_affine,
        )[0]

    # do not provide pixel_size + bounds OR affine + shape
    # perhaps this should be a more specific type of exception?
    with pytest.raises(Exception):
        rasterize(example_shape)


    # attriubte is not a valid keyword
    with pytest.raises(KeyError):
        rasterize(
            example_shape, pixel_size=0.5, bounds=example_shape.bounds, attribute="abc"
        )


def test_bad_rasterize_output(example_shape, example_affine):

    # fiona throws exception here because file is not found
    # perhaps this should be a more specific type of exception?
    with pytest.raises(Exception):
        rasterize(
            "bad/path/to/file",
            pixel_size=0.5,
            bounds=example_shape.bounds
        )


def test_export_raster(example_raster, example_affine, example_path):

    export_raster(example_raster, example_affine, example_path)

    # test if file was created by export_raster at example_path
    assert os.path.exists(example_path)

    # open raster written to example_path and make sure the data matches
    with rasterio.open(example_path) as src:
        assert (src.read() == example_raster).all


def test_bad_export_raster(example_raster, example_affine, example_path):

    # TODO: pass bad raster to export_raster

    # Try passing a bad output datatype
    with pytest.raises(ValueError):
        export_raster(
            example_raster, example_affine, example_path, out_dtype="bad_dt42"
        )

    # TODO: pass bad nodata to export_raster


def test_convert_index_to_coords(example_affine):
    # Simple index with affine identity
    assert convert_index_to_coords((1, 2), Affine.identity()) == (2.5, -1.5)

    # Random index with example affine
    assert convert_index_to_coords((5, 8), example_affine) == (12.75, -7.25)


def test_calc_haversine_distance():
    # Test distance that should be zero
    assert calc_haversine_distance((0, -180), (180, 0)) == 0

    # More complex test calculation that requires every aspect of the function
    a = math.cos(math.pi / 2) * math.sqrt(2) / 8 + math.sin(math.pi / 8) ** 2
    expected_output = math.atan2(math.sqrt(a), math.sqrt(1 - a)) * 12742
    assert (
        calc_haversine_distance((math.pi, -90), (4 * (math.pi / 3), -45))
        == expected_output
    )

    # Make sure output is float
    assert isinstance(calc_haversine_distance((0, 0), (0, 0)), float)
