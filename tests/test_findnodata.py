import rasterio as rio
from rio_alpha.findnodata import determine_nodata
import hypothesis.strategies as st
from hypothesis import given, example
from hypothesis.extra.numpy import arrays
import numpy as np
import pytest
from scipy.stats import mode
from rio_alpha.findnodata import discover_ndv

from rio_alpha.utils import (
    _convert_rgb, _find_continuous_rgb,
    _group, _compute_continuous,
    _search_image_edge,
    _evaluate_count)


@pytest.fixture
def test_fixtures():
    src_path_ca = 'tests/fixtures/ca_chilliwack/2012_30cm_592_5452.tiny.tif'
    src_path_ca2 = 'tests/fixtures/ca_chilliwack/2012_30cm_594_5454.tiny.tif'

    with rio.open(src_path_ca) as src_ca:
        data_ca = np.rollaxis(src_ca.read(), 0, 3)

    with rio.open(src_path_ca2) as src_ca2:
        data_ca2 = np.rollaxis(src_ca2.read(), 0, 3)

    return data_ca, data_ca2


@pytest.fixture
def test_fixture_4_band():
    src_path_4_band = 'tests/fixtures/ca_chilliwack/' \
                      '13-1326-2805-test-2015-2012_30cm_592_5450.tif'

    return src_path_4_band


@pytest.fixture
def test_fixtures3():
    src_path_dk = 'tests/fixtures/dk_all/320_ECW_UTM32-EUREF89.tiny.tif'
    src_path_fi = 'tests/fixtures/fi_all/W4441A.tiny.tif'

    with rio.open(src_path_dk) as src_dk:
        data_dk = np.rollaxis(src_dk.read(), 0, 3)

    with rio.open(src_path_fi) as src_fi:
        data_fi = np.rollaxis(src_fi.read(), 0, 3)

    return data_dk, data_fi


def test_determine_nodata_return_alpha(test_fixture_4_band):
    src_path = test_fixture_4_band
    output = determine_nodata(src_path, None, False, False, False)
    assert output == 'alpha'


arr_str2 = arrays(np.uint8, (8, 8, 3),
                  elements=st.integers(
                  min_value=1,
                  max_value=1))


@given(arr_str2)
def test_discover_ndv_list_three(arr_str2):
    candidates = discover_ndv(arr_str2, debug=False, verbose=True)
    mode_vals = mode(_convert_rgb(arr_str2)[1])
    candidate_original = [int((mode_vals[0])[0, i]) for i in range(3)]
    candidate_continuous, arr = _compute_continuous(
                                    _convert_rgb(arr_str2)[0], 1)
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
    candidate_continuous, arr = _compute_continuous(
                                    _convert_rgb(arr_str2)[0], 1)
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
    candidate_continuous, arr = _compute_continuous(
                                    _convert_rgb(arr_str2)[0], 1)
    candidate_list = \
        [i for i, j in zip(candidate_original,
                           candidate_continuous)
         if i == j]
    assert candidates == ''
