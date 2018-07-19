import rasterio
import hypothesis.strategies as st
from hypothesis import given
from hypothesis.extra.numpy import arrays
import numpy as np
from rio_alpha.islossy import count_ndv_regions


def test_count_ndv_regions_should_return_0():
    with rasterio.open(
        "tests/fixtures/ca_chilliwack/" "2012_30cm_594_5450.tiny.tif"
    ) as src:
        img = src.read()
        ndv = (0, 0, 0)
        assert count_ndv_regions(img, ndv) == 0


def test_count_ndv_regions_should_return_results():
    with rasterio.open(
        "tests/fixtures/ca_chilliwack/" "2012_30cm_594_5450.tiny.tif"
    ) as src:
        img = src.read()
        ndv = (255, 255, 255)
        assert count_ndv_regions(img, ndv) == 14666


@given(
    st.lists(
        st.integers(min_value=1, max_value=np.iinfo("uint16").max),
        min_size=3,
        max_size=3,
    ),
    arrays(
        np.uint16,
        (3, 10, 10),
        elements=st.integers(min_value=0, max_value=np.iinfo("uint16").max),
    ),
)
def test_count_ndv_regions(ndv, img):
    n_labels = count_ndv_regions(img, ndv)
    assert isinstance(n_labels, int)


arr_str = arrays(
    np.uint8,
    (8, 8, 3),
    elements=st.integers(min_value=1, max_value=np.iinfo("uint8").max),
)
