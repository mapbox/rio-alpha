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
    _convert_rgb, _find_continuous_rgb,
    _group, _compute_continuous,
    _search_image_edge)



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


@given(arrays(np.uint8, (6, 8, 3),
             elements=st.integers(
             min_value=1,
             max_value=np.iinfo('uint8').max)))
def test_convert_rgb_dim_zero(rgb_orig):
    rgb_mod_flat = _convert_rgb(rgb_orig)
    assert np.array_equal(rgb_mod_flat[1],
                    rgb_orig.reshape(
                        rgb_orig.shape[0]*rgb_orig.shape[1],
                        rgb_orig.shape[-1]))


@given(arr_str,
       st.integers(min_value=0, max_value=1))
def test_find_continuous_rgb(arr_str, num_axis):
    diff_array = np.diff(arr_str, axis=num_axis)
    diff_array = np.insert(diff_array, 0,[99, 99, 99], axis=num_axis)
    val_list = (arr_str[diff_array == [0, 0, 0]]).tolist()
    assert sorted(_find_continuous_rgb(arr_str, num_axis)) == sorted(val_list)


@given(st.integers(min_value=4, max_value=30))
def test_group(m):
    lst = range(1, m)
    arr = np.asarray(zip(*[lst[i::3] for i in range(3)]))
    mode_vals = mode(arr)
    cont = [int((mode_vals[0])[0, i]) for i in range(3)]
    test = []
    assert sorted(cont) == sorted(_group(lst, 3, test)[0])


@given(st.lists(
            st.integers(),
            max_size=2
        ),
       st.integers(min_value=0, max_value=1))
def test_group_error(lst, loc):
    with pytest.raises(IndexError):
        test = []
        _group(lst, 3, test)


@given(arr_str, 
       st.integers(min_value=0, max_value=1))
def test_compute_continuous(rgb_mod, loc):
    if len(_find_continuous_rgb(rgb_mod, loc)) < 3:
        with pytest.raises(IndexError):
            _compute_continuous(rgb_mod, loc)[0]
    else:
        assert _compute_continuous(rgb_mod, loc)[0] == \
            _group(_find_continuous_rgb(rgb_mod, loc),
                      3,
                      [])[0]


arr_str2 = arrays(np.uint8, (8, 8, 3),
              elements=st.integers(
              min_value=1,
              max_value=1))


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
def test_discover_ndv_list_less_three2(arr_str2):
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
    candidates = discover_ndv(arr_str2, debug=False, verbose=False)
    mode_vals = mode(_convert_rgb(arr_str2)[1])
    candidate_original = [int((mode_vals[0])[0, i]) for i in range(3)]
    candidate_continuous, arr = _compute_continuous(_convert_rgb(arr_str2)[0], 1)
    candidate_list = \
        [i for i, j in zip(candidate_original,
                           candidate_continuous)
         if i == j]
    assert candidates == ''
