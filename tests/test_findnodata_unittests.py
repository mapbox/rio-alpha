
import pytest
import numpy as np
import rasterio as rio
from rio_alpha.findnodata import determine_nodata

from rio_alpha.utils import (
    _parse_single, _parse_ndv,
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


def test_return_alpha(test_fixture_4_band):
    src_path = test_fixture_4_band
    output = determine_nodata(src_path, None, False, False, False)
    assert output == 'alpha'


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
    output = _evaluate_count(lst1, lst2, True)

    assert output == "None"


def test_evaluate_count_none():
    lst1 = [17, 15]
    lst2 = [26, 28]
    output = _evaluate_count(lst1, lst2, False)

    assert output == ""
