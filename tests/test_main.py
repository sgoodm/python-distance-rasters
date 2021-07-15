import os
import math
from affine import Affine
import pytest
import numpy as np
from distancerasters import build_distance_array


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


def test_build_distance_array(example_raster_array, example_affine):

    built_array = build_distance_array(example_raster_array, affine=example_affine)

    assert 1


def test_bad_build_distance_array(example_raster_array):
    with pytest.raises(TypeError):
        # Pass build_distance_array a 2D list
        build_distance_array([[0, 1], [1, 0]])

        # Pass build_distance_array a bad affine
        build_distance_array(np.array([[0, 1], [1, 0]]), affine="not_an_affine")

    # TODO: Pass a bad conditional
