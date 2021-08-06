import os
import math
from affine import Affine
import pytest
import numpy as np
from distancerasters import DistanceRaster
from distancerasters.utils import calc_haversine_distance


@pytest.fixture
def example_raster_array():
    arr = [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    return np.array(arr)


@pytest.fixture
def example_affine():
    return Affine(1.5, 1.0, 0.0, 1.0, 1.5, 1.0)


@pytest.fixture
def example_path():
    return "tests/testdata/build_distance_array_raster"


def test_build_distance_array(example_raster_array, example_affine, example_path):

    built_array = DistanceRaster(example_raster_array).dist_array

    # [1][1] was 1 in the passed array
    # The distance should be 0
    assert built_array[1][1] == 0

    # [1][2] was a single unit away from two 1 elements
    # This distance should be 1
    assert built_array[1][2] == 1

    assert built_array[1][3] == math.sqrt(2)

    assert built_array[0][3] == math.sqrt(5)


def test_build_distance_array_output(example_raster_array, example_affine, example_path):

    # Delete any previous test export, if it exists
    if os.path.isfile(example_path):
        os.remove(example_path)

    built_array = DistanceRaster(
        example_raster_array, affine=example_affine, output_path=example_path
    )
    # export_raster should have been called, and wrote output to example_path
    # perhaps we should more rigorously check if the exported raster is correct?
    assert os.path.exists(example_path)


def test_build_distance_array_with_affine(example_raster_array, example_affine):

    built_array = DistanceRaster(example_raster_array, affine=example_affine).dist_array

    # Testing the same array elements as the last function did

    assert built_array[1][1] == 0

    assert built_array[0][1] == 1.5 * 111.321 * 1000

    assert (
        built_array[1][3]
        == calc_haversine_distance((5.25, -1.25), (3.75, -2.75)) * 1000
    )

    assert (
        built_array[0][3] == calc_haversine_distance((5.25, 0.25), (2.25, -1.25)) * 1000
    )


def test_bad_build_distance_array(example_raster_array):
    with pytest.raises(TypeError):
        # Pass DistanceRaster a 2D list
        DistanceRaster([[0, 1], [1, 0]])

    with pytest.raises(TypeError):
        # Pass DistanceRaster a bad affine
        DistanceRaster(example_raster_array, affine="not_an_affine")

    # perhaps this should be a more specific type of exception?
    with pytest.raises(Exception):
        # Pass DistanceRaster an output without an affine
        DistanceRaster(example_raster_array, output_path="just_output")

    # perhaps this should be a more specific type of exception?
    with pytest.raises(Exception):
        # Pass DistanceRaster an uncallable conditional
        DistanceRaster(example_raster_array, conditional="not_a_function")
