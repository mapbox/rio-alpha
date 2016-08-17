import click
import pytest
import logging
from click.testing import CliRunner

from rio_alpha.scripts.cli import islossy


def test_cli_usage():
    result = CliRunner().invoke(islossy, [
        'tests/fixtures/dne.tif'
    ])
    assert result.exit_code == 2
    assert 'Invalid value for "input"' in result.output


def test_lossy_single_value_ndv():
    result = CliRunner().invoke(islossy, [
        'tests/fixtures/ca_chilliwack/2012_30cm_594_5450.tiny.tif',
        '--ndv', '255'
    ])
    assert result.exit_code == 0
    assert result.output.strip('\n') == "--lossy lossy"


def test_lossy_single_value_ndv_fail():
    runner = CliRunner()

    result = runner.invoke(islossy, [
        'tests/fixtures/ca_chilliwack/2012_30cm_594_5450.tiny.tif',
        '--ndv', 'ndv'
    ])

    assert result.exit_code != 0


def test_lossy_three_value_ndv():
    runner = CliRunner()

    result = runner.invoke(islossy, [
        'tests/fixtures/ca_chilliwack/2012_30cm_594_5450.tiny.tif',
        '--ndv', '[255, 255, 255]'
    ])
    assert result.exit_code == 0
    assert result.output.strip('\n') == "--lossy lossy"

    result = runner.invoke(islossy, [
        'tests/fixtures/dk_all/450_ECW_UTM32-EUREF89.tiny.tif',
        '--ndv', '[255, 255, 255]'
    ])
    assert result.exit_code == 0
    assert result.output.strip('\n') == "--lossy lossy"

    result = runner.invoke(islossy, [
        'tests/fixtures/fi_all/W4441A.tiny.tif',
        '--ndv', '[255, 255, 255]'
    ])
    assert result.exit_code == 0
    assert result.output.strip('\n') == "--lossy lossy"


def test_lossy_three_value_ndv_fail():
    runner = CliRunner()

    result = runner.invoke(islossy, [
        'tests/fixtures/ca_chilliwack/2012_30cm_594_5450.tiny.tif',
        '--ndv', '[255, 255, \'ndv\']'
    ])

    assert result.exit_code != 0


def test_notlossy_single_value_ndv():
    result = CliRunner().invoke(islossy, [
        'tests/fixtures/ca_chilliwack/2012_30cm_592_5452.tiny.tif',
        '--ndv', '255'
    ])
    assert result.exit_code == 0
    assert result.output.strip('\n') == ""


def test_notlossy_diff_three_value_ndv():
    runner = CliRunner()

    result = runner.invoke(islossy, [
        'tests/fixtures/dk_all/320_ECW_UTM32-EUREF89.tiny.tif',
        '--ndv', '[18, 51, 62]'
    ])
    assert result.exit_code == 0
    assert result.output.strip('\n') == ""


def test_nolossy_same_three_value_ndv():
    runner = CliRunner()
    result = runner.invoke(islossy, [
        'tests/fixtures/ca_chilliwack/2012_30cm_592_5452.tiny.tif',
        '--ndv', '[255, 255, 255]'
    ])
    assert result.exit_code == 0
    assert result.output.strip('\n') == ""
