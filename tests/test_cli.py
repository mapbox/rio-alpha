import click
import pytest
from click.testing import CliRunner

from rio_alpha.scripts.cli import islossy


def test_cli_empty_files():
    pass
    # test_cmd 0 0 0 empty.tif "Could not open file"
    # test_cmd 0 0 0 prep/13-3032-4670-test-2014-unhappy.tif "Could not open file"


def test_cli_expected_outputs():
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
