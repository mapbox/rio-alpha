import click
import pytest
from click.testing import CliRunner
import warnings

from rio_alpha.scripts.cli import alpha, islossy, findnodata


def test_cli_alpha():
    runner = CliRunner()
    result = runner.invoke(alpha)
    assert 'Usage: alpha' in result.output


def test_cli_missing_input():
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


def test_findnodata_default_success():
    runner = CliRunner()
    result = runner.invoke(findnodata,[
        'tests/fixtures/dk_all/320_ECW_UTM32-EUREF89.tiny.tif',
        ])
    assert result.exit_code == 0
    assert result.output.strip('\n') == ""


def test_findnodata_read_src_ndv():
    runner = CliRunner()
    result = runner.invoke(findnodata,[
        'tests/fixtures/ca_chilliwack/2012_30cm_594_5450_src_ndv.tiny.tif',
        ])
    assert result.exit_code == 0
    assert result.output.strip('\n') == "255"


def test_findnodata_read_4_bands():
    runner = CliRunner()
    result = runner.invoke(findnodata,[
        'tests/fixtures/ca_chilliwack/'
        '13-1326-2805-test-2015-2012_30cm_592_5450.tif'
        ])
    assert result.exit_code == 0
    assert result.output.strip('\n') == "alpha"


def test_findnodata_discovery_success():
    runner = CliRunner()
    result = runner.invoke(findnodata,[
        'tests/fixtures/dk_all/320_ECW_UTM32-EUREF89.tiny.tif',
        '--discovery'])
    assert result.exit_code == 0
    assert result.output.strip('\n') == "18 51 62"


def test_findnodata_user_nodata_success():
    runner = CliRunner()
    result = runner.invoke(findnodata, [
        'tests/fixtures/dk_all/320_ECW_UTM32-EUREF89.tiny.tif',
        '--user_nodata', '255 255 255'])
    assert result.exit_code == 0
    assert result.output.strip('\n') == '255 255 255'


def test_findnodata_verbose_success():
    runner = CliRunner()
    result = runner.invoke(findnodata, [
        'tests/fixtures/fi_all/W4441A.tiny.tif',
        '--discovery', '--verbose'])
    assert result.exit_code == 0
    assert result.output.strip('\n') == '255 255 255'


def test_findnodata_debug_success():
    runner = CliRunner()
    result = runner.invoke(findnodata, [
        'tests/fixtures/fi_all/W4441A.tiny.tif', 
        '--discovery', '--debug'])
    warnings.filterwarnings("ignore", module="matplotlib")
    assert result.exit_code == 0
    assert 'Original image ndv candidate: [255, 255, 255]\n' \
        'Filtered image ndv candidate: [255, 255, 255]\n' in result.output
