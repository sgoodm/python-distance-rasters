import os
import math
import pytest
import numpy as np
from distancerasters import build_distance_array


@pytest.fixture
def example_raster_array():
    return [[0, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]]

def test_build_distance_array(example_raster_array):

    raster_np_array = np.array(example_raster_array)
    built_array = build_distance_array(raster_np_array)

    # [1][1] was 1 in the passed array
    # The distance should be 0
    assert built_array[1][1] == 0

    # [1][2] was a single unit away from two 1 elements
    # This distance should be 1
    assert built_array[1][2] == 1

    assert built_array[1][3] == math.sqrt(2)

def test_bad_build_distance_array(example_raster_array):
    # Pass build_distance_array a 2D list
    with pytest.raises(TypeError):
        build_distance_array([[0, 1], [1, 0]])
