import click
import pytest
from click.testing import CliRunner

from rio_alpha.scripts.cli import islossy


def test_cli_expected_failures():
    runner = CliRunner()

    result = runner.invoke(islossy, [
        'tests/fixtures/dne.tif'
    ])
    assert result.exit_code == 2
    assert 'Invalid value for "input"' in result.output


def test_cli_expected_successes():
    runner = CliRunner()

    result = runner.invoke(islossy, [
        'tests/fixtures/ca_chilliwack/2012_30cm_592_5452.tiny.tif',
        '--ndv', '[255, 255, 255]'
    ])
    assert result.exit_code == 0
    assert result.output.strip('\n') == ""

    result = runner.invoke(islossy, [
        'tests/fixtures/ca_chilliwack/2012_30cm_594_5450.tiny.tif',
        '--ndv', '[255, 255, 255]'
    ])
    assert result.exit_code == 0
    assert result.output.strip('\n') == "--lossy lossy"

    result = runner.invoke(islossy, [
        'tests/fixtures/ca_chilliwack/2012_30cm_594_5452.tiny.tif',
        '--ndv', '[255, 255, 255]'
    ])
    assert result.exit_code == 0
    assert result.output.strip('\n') == "--lossy lossy"

    result = runner.invoke(islossy, [
        'tests/fixtures/ca_chilliwack/2012_30cm_594_5454.tiny.tif',
        '--ndv', '[255, 255, 255]'
    ])
    assert result.exit_code == 0
    assert result.output.strip('\n') == "--lossy lossy"

    result = runner.invoke(islossy, [
        'tests/fixtures/ca_kamloops/2012_6156D.tiny.tif',
        '--ndv', '[255, 255, 255]'
    ])
    assert result.exit_code == 0
    assert result.output.strip('\n') == "--lossy lossy"

    result = runner.invoke(islossy, [
        'tests/fixtures/dk_all/320_ECW_UTM32-EUREF89.tiny.tif',
        '--ndv', '[18, 51, 62]'
    ])
    assert result.exit_code == 0
    assert result.output.strip('\n') == ""

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


