import re
import json

import hypothesis.strategies as st
from hypothesis import given, example
from hypothesis.extra.numpy import arrays
import numpy as np
import pytest

from rio_alpha.utils import _parse_single, _parse_ndv
from rio_alpha.islossy import count_ndv_regions


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
