import hypothesis.strategies as st
from hypothesis import given, example
from hypothesis.extra.numpy import arrays
import rasterio as rio

import numpy as np
import pytest
from scipy.stats import mode

from rio_alpha.utils import (
    _parse_single, _parse_ndv,
    _convert_rgb, _find_continuous_rgb,
    _group, _compute_continuous,
    _search_image_edge,
    _evaluate_count)


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
    diff_array = np.insert(diff_array, 0, [99, 99, 99], axis=num_axis)
    val_list = (arr_str[diff_array == [0, 0, 0]]).tolist()
    assert sorted(_find_continuous_rgb(arr_str, num_axis)) == sorted(val_list)


@given(st.integers(min_value=4, max_value=30))
def test_group(m):
    lst = range(1, m)
    arr = np.asarray(list(zip(*[lst[i::3] for i in range(3)])))
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


def test_search_image_edge_ca(test_fixtures):
    data_ca, data_ca2 = test_fixtures
    data_ca_mod = _convert_rgb(data_ca)[0]

    candidate_original = [191, 185, 171]
    candidate_continuous = [172, 172, 172]

    rgb_mod = np.copy(data_ca_mod)
    top_row = rgb_mod[0, :, :]
    bottom_row = rgb_mod[-1, :, :]
    first_col = rgb_mod[:, 0, :]
    last_col = rgb_mod[:, -1, :]
    img_edge = np.concatenate(
                    (top_row, last_col, bottom_row, first_col),
                    axis=0
                )
    arr = _compute_continuous(rgb_mod, 0)[-1]
    full = [len(np.transpose(np.where((img_edge == candidate).all(axis=1))))
            for candidate in (candidate_original, candidate_continuous)]

    cont = [len(np.transpose(np.where((arr == candidate).all(axis=1))))
            for candidate in (candidate_original, candidate_continuous)]

    assert img_edge.shape[0] == rgb_mod.shape[0] * 4
    assert full == _search_image_edge(rgb_mod,
                                      candidate_original,
                                      candidate_continuous)[0]
    assert cont == _search_image_edge(rgb_mod,
                                      candidate_original,
                                      candidate_continuous)[1]


def test_search_image_edge_ca2(test_fixtures):
    data_ca, data_ca2 = test_fixtures
    data_ca2_mod = _convert_rgb(data_ca2)[0]

    candidate_original = [255, 255, 255]
    candidate_continuous = [255, 255, 250]

    rgb_mod = np.copy(data_ca2_mod)
    top_row = rgb_mod[0, :, :]
    bottom_row = rgb_mod[-1, :, :]
    first_col = rgb_mod[:, 0, :]
    last_col = rgb_mod[:, -1, :]
    img_edge = np.concatenate(
                    (top_row, last_col, bottom_row, first_col),
                    axis=0
                )
    arr = _compute_continuous(rgb_mod, 0)[-1]
    full = [len(np.transpose(np.where((img_edge == candidate).all(axis=1))))
            for candidate in (candidate_original, candidate_continuous)]

    cont = [len(np.transpose(np.where((arr == candidate).all(axis=1))))
            for candidate in (candidate_original, candidate_continuous)]

    assert img_edge.shape[0] == rgb_mod.shape[0] * 4
    assert full == [348, 0]
    assert cont == [12306, 0]


def test_evaluate_count_original():
    lst1 = [17, 15]
    lst2 = [28, 26]
    output = _evaluate_count(lst1, lst2, False)

    assert output == lst1


def test_evaluate_count_continuous():
    lst1 = [20, 25]
    lst2 = [26, 28]
    output = _evaluate_count(lst1, lst2, False)

    assert output == lst2


def test_evaluate_count_none():
    lst1 = [17, 15]
    lst2 = [26, 28]
    output = _evaluate_count(lst1, lst2, False)

    assert output == ""
