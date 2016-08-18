import pytest
import rasterio as rio

from rio_alpha.islossy import count_ndv_regions


def test_count_ndv_regions_should_return_0():
    with rio.open('tests/fixtures/ca_chilliwack/2012_30cm_594_5450.tiny.tif') as src:
        img = src.read()
        assert count_ndv_regions(img, 0) == 0


def test_count_ndv_regions_should_return_results():
    with rio.open('tests/fixtures/ca_chilliwack/2012_30cm_594_5450.tiny.tif') as src:
        img = src.read()
        assert count_ndv_regions(img, 255) == 14666
