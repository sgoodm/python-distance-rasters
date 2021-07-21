import os
import math
from affine import Affine
import pytest
import numpy as np
from distancerasters import build_distance_array
from distancerasters.utils import calc_haversine_distance


@pytest.fixture
def example_raster_array():
    arr = [[0, 0, 0, 0],
           [0, 1, 0, 0],
           [0, 0, 1, 0],
           [0, 0, 0, 1]]
    return np.array(arr)


@pytest.fixture
def example_affine():
    return Affine(1.5, 1.0, 0.0, 1.0, 1.5, 1.0)


def test_build_distance_array(example_raster_array):

    built_array = build_distance_array(example_raster_array)

    # [1][1] was 1 in the passed array
    # The distance should be 0
    assert built_array[1][1] == 0

    # [1][2] was a single unit away from two 1 elements
    # This distance should be 1
    assert built_array[1][2] == 1

    assert built_array[1][3] == math.sqrt(2)

    assert built_array[0][3] == math.sqrt(5)


def test_build_distance_array_with_affine(example_raster_array, example_affine):

    built_array = build_distance_array(example_raster_array, affine=example_affine)

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
        # Pass build_distance_array a 2D list
        build_distance_array([[0, 1], [1, 0]])

    with pytest.raises(TypeError):
        # Pass build_distance_array a bad affine
        build_distance_array(np.array([[0, 1], [1, 0]]), affine="not_an_affine")

    # Should this be a more specific type of error?
    with pytest.raises(Exception):
        # Pass build_distance_array an output without an affine
        build_distance_array(np.array([[0, 1], [1, 0]]), output="just_output")

    # TODO: Pass a bad conditional
