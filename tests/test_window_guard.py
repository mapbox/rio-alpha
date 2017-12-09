"""Window guard tests"""

from unittest.mock import patch

import pytest

import rio_alpha.alpha


class MockWindow:
    pass


def test_import_window():
    windows_mod = pytest.importorskip("rasterio.windows")
    window = windows_mod.Window(0, 0, 10, 10)
    assert rio_alpha.alpha.window_guard(window) == window


@patch('rio_alpha.alpha.Window', MockWindow)
def test_window():
    window = MockWindow()
    assert rio_alpha.alpha.window_guard(window) == window


def test_tuple_convert():
    windows_mod = pytest.importorskip("rasterio.windows")
    window = ((1, 2), (3, 4))
    assert rio_alpha.alpha.window_guard(window) == windows_mod.Window(3, 1, 1, 1)
