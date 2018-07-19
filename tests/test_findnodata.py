import rasterio as rio
import hypothesis.strategies as st
from hypothesis import given
from hypothesis.extra.numpy import arrays
import numpy as np
import pytest
from rio_alpha.findnodata import discover_ndv, determine_nodata

from rio_alpha.utils import _convert_rgb, _compute_continuous


@pytest.fixture
def test_fixtures():
    src_path_ca = "tests/fixtures/ca_chilliwack/2012_30cm_592_5452.tiny.tif"
    src_path_ca2 = "tests/fixtures/ca_chilliwack/2012_30cm_594_5454.tiny.tif"

    return src_path_ca, src_path_ca2


@pytest.fixture
def test_fixture_4_band():
    src_path_4_band = "tests/fixtures/ca_chilliwack/" "13-1326-2805-test-2015-2012_30cm_592_5450.tif"

    return src_path_4_band


@pytest.fixture
def test_fixtures3():
    src_path_dk = "tests/fixtures/dk_all/320_ECW_UTM32-EUREF89.tiny.tif"
    src_path_fi = "tests/fixtures/fi_all/W4441A.tiny.tif"

    with rio.open(src_path_dk) as src_dk:
        data_dk = np.rollaxis(src_dk.read(), 0, 3)

    with rio.open(src_path_fi) as src_fi:
        data_fi = np.rollaxis(src_fi.read(), 0, 3)

    return data_dk, data_fi


def test_determine_nodata_return_alpha(test_fixture_4_band):
    src_path = test_fixture_4_band
    output = determine_nodata(src_path, None, False, False, False)
    assert output == "alpha"


def test_determine_nodata_return_none(test_fixtures):
    src_path1, src_path2 = test_fixtures
    output1 = determine_nodata(src_path1, None, False, False, False)
    output2 = determine_nodata(src_path2, None, False, False, False)
    assert output1 == ""
    assert output2 == ""


arr_str2 = arrays(np.uint8, (8, 8, 3), elements=st.integers(min_value=1, max_value=1))


@given(arr_str2)
def test_discover_ndv_list_three(arr_str2):
    candidates = discover_ndv(arr_str2, debug=False, verbose=True)
    candidate_continuous, arr = _compute_continuous(_convert_rgb(arr_str2)[0], 1)
    assert candidates == [1, 1, 1]


@given(arr_str2)
def test_discover_ndv_list_less_three(arr_str2):
    cons_arr = np.array(
        [
            [1, 1, 1],
            [1, 1, 1],
            [1, 2, 1],
            [1, 2, 1],
            [1, 2, 1],
            [1, 2, 1],
            [1, 1, 1],
            [1, 2, 1],
        ]
    )

    cons_arr2 = np.array(
        [
            [1, 1, 1],
            [1, 2, 1],
            [1, 1, 1],
            [1, 2, 1],
            [1, 1, 1],
            [1, 2, 1],
            [1, 1, 1],
            [1, 2, 1],
        ]
    )

    arr_str2[0] = cons_arr
    arr_str2[1:] = cons_arr2
    candidates = discover_ndv(arr_str2, debug=False, verbose=True)
    candidate_continuous, arr = _compute_continuous(_convert_rgb(arr_str2)[0], 1)
    assert candidates == "None"


@given(arr_str2)
def test_discover_ndv_list_less_three2(arr_str2):
    cons_arr = np.array(
        [
            [1, 1, 1],
            [1, 1, 1],
            [1, 2, 1],
            [1, 2, 1],
            [1, 2, 1],
            [1, 2, 1],
            [1, 1, 1],
            [1, 2, 1],
        ]
    )

    cons_arr2 = np.array(
        [
            [1, 1, 1],
            [1, 2, 1],
            [1, 1, 1],
            [1, 2, 1],
            [1, 1, 1],
            [1, 2, 1],
            [1, 1, 1],
            [1, 2, 1],
        ]
    )

    arr_str2[0] = cons_arr
    arr_str2[1:] = cons_arr2
    candidates = discover_ndv(arr_str2, debug=False, verbose=False)
    candidate_continuous, arr = _compute_continuous(_convert_rgb(arr_str2)[0], 1)
    assert candidates == ""
