import re
import json

import hypothesis.strategies as st
from hypothesis import given, example
from hypothesis.extra.numpy import arrays
import numpy as np
import pytest
from scipy.stats import mode

from rio_alpha.islossy import count_ndv_regions
from rio_alpha.findnodata import discover_ndv
from rio_alpha.utils import (
    _parse_single, _parse_ndv,
    _convert_rgb, _compute_continuous)



@given(st.integers(
        min_value=1,
        max_value=np.iinfo('uint16').max))
def test_parse_single(n):
    assert isinstance(_parse_single(n), float)
    assert float(n) == _parse_single(n)


@given(st.text(alphabet=['a', 'b', 'c'], min_size=1))
@example("Hello world")
def test_parse_single_fail(t):
    with pytest.raises(ValueError) as excinfo:
        _parse_single(t)
    assert 'not a valid nodata value' in str(excinfo.value)


@given(st.lists(
            st.integers(
                min_value=1,
                max_value=np.iinfo('uint16').max),
            min_size=3,
            max_size=3))
def test_parse_ndv(ndv):
    ndvals = _parse_ndv(str(ndv), len(ndv))
    assert [float(n) for n in ndv] == ndvals
    assert isinstance(ndvals[0], float)


@given(st.lists(
            st.integers(
                min_value=1,
                max_value=np.iinfo('uint16').max),
            min_size=4))
def test_parse_ndv_fail_bands(ndv):
    with pytest.raises(ValueError) as excinfo:
        _parse_ndv(str(ndv), 3)
    assert 'does not match band count of' in str(excinfo.value)


@given(st.lists(
            st.integers(
                min_value=1,
                max_value=np.iinfo('uint16').max),
            min_size=3,
            max_size=3),
       arrays(
           np.uint16, (3, 10, 10),
                elements=st.integers(
                    min_value=0,
                    max_value=np.iinfo('uint16').max)))
def test_count_ndv_regions(ndv, img):
    n_labels = count_ndv_regions(img, ndv)
    assert isinstance(n_labels, int)

arr_str = arrays(np.uint8, (8, 8, 3),
              elements=st.integers(
              min_value=1,
              max_value=np.iinfo('uint8').max))


@given(arr_str)
def test_convert_rgb(rgb_orig):
    rgb_mod_flat = _convert_rgb(rgb_orig)
    assert np.array_equal(rgb_mod_flat[1],
                    rgb_orig.reshape(
                        rgb_orig.shape[0]*rgb_orig.shape[1],
                        rgb_orig.shape[-1]))


arr_str2 = arrays(np.uint8, (8, 8, 3),
              elements=st.integers(
              min_value=1,
              max_value=1))

@given(arr_str2)
def test_discover_ndv_list_less_three(arr_str2):
    cons_arr = np.array([[1, 1, 1],
                      [1, 1, 1],
                      [1, 2, 1],
                      [1, 2, 1],
                      [1, 2, 1],
                      [1, 2, 1],
                      [1, 1, 1],
                      [1, 2, 1]])

    cons_arr2 = np.array([[1, 1, 1],
                         [1, 2, 1],
                         [1, 1, 1],
                         [1, 2, 1],
                         [1, 1, 1],
                         [1, 2, 1],
                         [1, 1, 1],
                         [1, 2, 1]])

    arr_str2[0] = cons_arr
    arr_str2[1:] = cons_arr2
    candidates = discover_ndv(arr_str2, debug=False, verbose=True)
    mode_vals = mode(_convert_rgb(arr_str2)[1])
    candidate_original = [int((mode_vals[0])[0, i]) for i in range(3)]
    candidate_continuous, arr = _compute_continuous(_convert_rgb(arr_str2)[0], 1)
    candidate_list = \
        [i for i, j in zip(candidate_original,
                           candidate_continuous)
         if i == j]
    assert candidates == 'None'


@given(arr_str2)
def test_discover_ndv_list_three(arr_str2):
    candidates = discover_ndv(arr_str2, debug=False, verbose=True)
    mode_vals = mode(_convert_rgb(arr_str2)[1])
    candidate_original = [int((mode_vals[0])[0, i]) for i in range(3)]
    candidate_continuous, arr = _compute_continuous(_convert_rgb(arr_str2)[0], 1)
    candidate_list = \
        [i for i, j in zip(candidate_original,
                           candidate_continuous)
         if i == j]
    assert candidates == [1, 1, 1]
