from affine import Affine
import click
import pytest
import numpy as np
import rasterio as rio
from rasterio.warp import reproject, Resampling
from rio_alpha.alpha_non_lossy import (
    add_alpha_non_lossy, calc_alpha)


def affaux(up):
    return Affine(1, 0, 0, 0, -1, 0), Affine(up, 0, 0, 0, -up, 0)


def upsample_array(bidx, up, fr, to):
    upBidx = np.empty(
        (bidx.shape[0] * up, bidx.shape[1] * up), dtype=bidx.dtype)

    reproject(
        bidx, upBidx,
        src_transform=fr,
        dst_transform=to,
        src_crs="EPSG:3857",
        dst_crs="EPSG:3857",
        resampling=Resampling.bilinear)

    return upBidx


def flex_compare(r1, r2, thresh=10):
    upsample = 4
    r1 = r1[::upsample]
    r2 = r2[::upsample]
    toAff, frAff = affaux(upsample)
    r1 = upsample_array(r1, upsample, frAff, toAff)
    r2 = upsample_array(r2, upsample, frAff, toAff)
    tdiff = np.abs(r1.astype(np.float64) - r2.astype(np.float64))
    click.echo('{0} values exceed the threshold'
               'difference with a max variance of {1}'.format(
                  np.sum(tdiff > thresh), tdiff.max()), err=True)
    return not np.any(tdiff > thresh)


@pytest.fixture
def test_var():
    src_path1 = 'tests/fixtures/ca_chilliwack/' \
                '2012_30cm_592_5454.tiled.tiny.tif'

    return src_path1


def test_(test_var, capfd):
    src_path = test_var
    dst_path = '/tmp/alpha_non_lossy_1.tif'
    expected_path = 'tests/expected/expected_alpha/2012_30cm_592_5454.tiny.tif'
    ndv = [255, 255, 255]
    blocksize = None
    debug = False
    processes = 1

    add_alpha_non_lossy(src_path, dst_path, ndv,
                        blocksize, debug, processes)
    out, err = capfd.readouterr()

    with rio.open(dst_path) as created:
        with rio.open(expected_path) as expected:
            assert flex_compare(created.read(), expected.read())
