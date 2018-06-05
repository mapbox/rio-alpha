"""Window guard tests"""

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import pytest

import rio_alpha.alpha


class MockWindow:
    pass


def test_import_window():
    window_cls = pytest.importorskip("rasterio.windows.Window")
    window = window_cls(0, 0, 10, 10)
    assert rio_alpha.alpha.window_guard(window) == window


@patch("rio_alpha.alpha.Window", MockWindow)
def test_window():
    window = MockWindow()
    assert rio_alpha.alpha.window_guard(window) == window


def test_tuple_convert():
    window_cls = pytest.importorskip("rasterio.windows.Window")
    window = ((1, 2), (3, 4))
    assert rio_alpha.alpha.window_guard(window) == window_cls(3, 1, 1, 1)
