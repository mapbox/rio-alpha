import rasterio as rio
import hypothesis.strategies as st
from hypothesis import given, example
from hypothesis.extra.numpy import arrays
import numpy as np
import pytest
from rio_alpha.alpha_mask import mask_exact


@pytest.fixture
def test_fixture():
    src_path = 'tests/fixtures/ca_chilliwack/2012_30cm_592_5452.tiny.tif'

    return src_path


def test_mask_exact1(test_fixture):
    with rio.open(test_fixture) as src:
        img = src.read()

    assert np.max(mask_exact(img, 255)) <= np.iinfo(img.dtype).max
    assert mask_exact(img, 255).dtype == img.dtype
    assert np.array_equal(np.invert(np.all(
                        np.rollaxis(img, 0, 3) == 255,
                        axis=2)).astype(img.dtype) * np.iinfo(img.dtype).max,
                        mask_exact(img, 255))


@pytest.fixture
def test_fixture2():
    src_path = 'tests/fixtures/dk_all/320_ECW_UTM32-EUREF89.tiny.tif'

    return src_path


def test_mask_exact2(test_fixture2):
    with rio.open(test_fixture2) as src:
        img = src.read()
    ndv = (18, 51, 62)
    assert np.max(mask_exact(img, ndv)) <= np.iinfo(img.dtype).max
    assert mask_exact(img, ndv).dtype == img.dtype
    assert np.array_equal(np.invert(np.all(
                        np.rollaxis(img, 0, 3) == ndv,
                        axis=2)).astype(img.dtype) * np.iinfo(img.dtype).max,
                        mask_exact(img, ndv))


arr1 = arrays(np.uint8, (3, 8, 10),
              elements=st.integers(
              min_value=1,
              max_value=1))


@given(arr1)
def test_mask_exact3(arr):
    for i in range(3):
        arr[i][-1][-1] = 0
    ndv = (0, 0, 0)

    assert np.max(mask_exact(arr, ndv)) <= np.iinfo(arr.dtype).max
    assert mask_exact(arr, ndv).dtype == arr.dtype
    assert np.array_equal(np.invert(np.all(
                            np.rollaxis(arr, 0, 3) == ndv,
                            axis=2)).astype(arr.dtype) *
                          np.iinfo(arr.dtype).max,
                          mask_exact(arr, ndv))


def test_mask_exact4():
    arr2 = np.random.randint(0, 255, (3, 10, 15))
    for i in range(3):
        arr2[i][-1][-1] = 255
        arr2[i][1][1] = 255
        arr2[i][2][2] = 255
    ndv = (255, 255, 255)

    assert np.array_equal(np.any(
                            np.rollaxis(arr2, 0, 3) != ndv,
                            axis=2),
                          mask_exact(arr2, ndv) / np.iinfo(arr2.dtype).max)
