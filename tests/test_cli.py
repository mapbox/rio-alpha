import os

import rasterio
import numpy as np
import click
import pytest
from click.testing import CliRunner
import warnings
from rasterio.enums import Compression

from rio_alpha.scripts.cli import alpha, islossy, findnodata


def test_cli_missing_input():
    result = CliRunner().invoke(islossy, ["tests/fixtures/dne.tif"])
    assert result.exit_code == 2
    assert 'Invalid value for "input"' in result.output


def test_cli_lossy_single_value_ndv():
    result = CliRunner().invoke(
        islossy,
        ["tests/fixtures/ca_chilliwack/2012_30cm_594_5450.tiny.tif", "--ndv", "255"],
    )
    assert result.exit_code == 0
    assert result.output.strip("\n") == "True"


def test_cli_lossy_single_value_ndv_fail():
    runner = CliRunner()
    result = runner.invoke(
        islossy,
        ["tests/fixtures/ca_chilliwack/2012_30cm_594_5450.tiny.tif", "--ndv", "ndv"],
    )

    assert result.exit_code != 0


def test_cli_lossy_three_value_ndv():
    runner = CliRunner()
    result = runner.invoke(
        islossy,
        [
            "tests/fixtures/ca_chilliwack/2012_30cm_594_5450.tiny.tif",
            "--ndv",
            "[255, 255, 255]",
        ],
    )
    assert result.exit_code == 0
    assert result.output.strip("\n") == "True"

    result = runner.invoke(
        islossy,
        [
            "tests/fixtures/dk_all/450_ECW_UTM32-EUREF89.tiny.tif",
            "--ndv",
            "[255, 255, 255]",
        ],
    )
    assert result.exit_code == 0
    assert result.output.strip("\n") == "True"

    result = runner.invoke(
        islossy, ["tests/fixtures/fi_all/W4441A.tiny.tif", "--ndv", "[255, 255, 255]"]
    )
    assert result.exit_code == 0
    assert result.output.strip("\n") == "True"


def test_cli_lossy_three_value_ndv_fail():
    runner = CliRunner()
    result = runner.invoke(
        islossy,
        [
            "tests/fixtures/ca_chilliwack/2012_30cm_594_5450.tiny.tif",
            "--ndv",
            "[255, 255, 'ndv']",
        ],
    )

    assert result.exit_code != 0


def test_cli_notlossy_single_value_ndv():
    result = CliRunner().invoke(
        islossy,
        ["tests/fixtures/ca_chilliwack/2012_30cm_592_5452.tiny.tif", "--ndv", "255"],
    )
    assert result.exit_code == 0
    assert result.output.strip("\n") == "False"


def test_cli_notlossy_diff_three_value_ndv():
    runner = CliRunner()
    result = runner.invoke(
        islossy,
        [
            "tests/fixtures/dk_all/320_ECW_UTM32-EUREF89.tiny.tif",
            "--ndv",
            "[18, 51, 62]",
        ],
    )
    assert result.exit_code == 0
    assert result.output.strip("\n") == "False"


def test_cli_nolossy_same_three_value_ndv():
    runner = CliRunner()
    result = runner.invoke(
        islossy,
        [
            "tests/fixtures/ca_chilliwack/2012_30cm_592_5452.tiny.tif",
            "--ndv",
            "[255, 255, 255]",
        ],
    )
    assert result.exit_code == 0
    assert result.output.strip("\n") == "False"


def test_cli_findnodata_default_success():
    runner = CliRunner()
    result = runner.invoke(
        findnodata, ["tests/fixtures/dk_all/320_ECW_UTM32-EUREF89.tiny.tif"]
    )
    assert result.exit_code == 0
    assert result.output.strip("\n") == ""


def test_cli_findnodata_read_src_ndv():
    runner = CliRunner()
    result = runner.invoke(
        findnodata, ["tests/fixtures/ca_chilliwack/2012_30cm_594_5450_src_ndv.tiny.tif"]
    )
    assert result.exit_code == 0
    assert result.output.strip("\n") == "255"


def test_cli_findnodata_read_4_bands():
    runner = CliRunner()
    result = runner.invoke(
        findnodata,
        [
            "tests/fixtures/ca_chilliwack/"
            "13-1326-2805-test-2015-2012_30cm_592_5450.tif"
        ],
    )
    assert result.exit_code == 0
    assert result.output.strip("\n") == "alpha"


def test_cli_findnodata_discovery_success():
    runner = CliRunner()
    result = runner.invoke(
        findnodata,
        ["tests/fixtures/dk_all/320_ECW_UTM32-EUREF89.tiny.tif", "--discovery"],
    )
    assert result.exit_code == 0
    assert result.output.strip("\n") == "[18, 51, 62]"


def test_cli_findnodata_nodiscovery_success():
    runner = CliRunner()
    result = runner.invoke(
        findnodata, ["tests/fixtures/dk_all/320_ECW_UTM32-EUREF89.tiny.tif"]
    )
    assert result.exit_code == 0
    assert result.output.strip("\n") == ""


def test_cli_findnodata_user_nodata_success():
    runner = CliRunner()
    result = runner.invoke(
        findnodata,
        [
            "tests/fixtures/dk_all/320_ECW_UTM32-EUREF89.tiny.tif",
            "--user_nodata",
            "[255, 255, 255]",
        ],
    )
    assert result.exit_code == 0
    assert result.output.strip("\n") == "[255, 255, 255]"


def test_cli_findnodata_verbose_success():
    runner = CliRunner()
    result = runner.invoke(
        findnodata,
        ["tests/fixtures/fi_all/W4441A.tiny.tif", "--discovery", "--verbose"],
    )
    assert result.exit_code == 0
    assert result.output.strip("\n") == "[255, 255, 255]"


def test_cli_findnodata_debug_success():
    runner = CliRunner()
    result = runner.invoke(
        findnodata, ["tests/fixtures/fi_all/W4441A.tiny.tif", "--discovery", "--debug"]
    )
    warnings.filterwarnings("ignore", module="matplotlib")
    assert result.exit_code == 0
    assert (
        "Original image ndv candidate: [255, 255, 255]\n"
        "Filtered image ndv candidate: [255, 255, 255]\n" in result.output
    )


def test_cli_alpha_default(tmpdir):
    output = str(tmpdir.join("test_alpha.tif"))
    runner = CliRunner()
    result = runner.invoke(
        alpha, ["tests/fixtures/dg_everest/everest_0430_R1C1.tiny.tif", output]
    )
    assert result.exit_code == 0
    assert os.path.exists(output)
    with rasterio.open(output) as out:
        assert out.count == 4
        assert out.dtypes[-1] == rasterio.uint8
        assert out.dtypes[0] == rasterio.uint8
        assert out.profile["tiled"] is False


def test_cli_alpha_ndv(tmpdir):
    output = str(tmpdir.join("test_alpha.tif"))
    runner = CliRunner()
    result = runner.invoke(
        alpha,
        [
            "tests/fixtures/dk_all/320_ECW_UTM32-EUREF89.tiny.tif",
            output,
            "--ndv",
            "[18, 51, 62]",
        ],
    )
    assert result.exit_code == 0
    assert os.path.exists(output)
    with rasterio.open(output) as out:
        assert out.count == 4
        assert out.dtypes[0] == rasterio.uint8


def test_cli_alpha_blocksize(tmpdir):
    output = str(tmpdir.join("test_alpha.tif"))
    runner = CliRunner()
    result = runner.invoke(
        alpha,
        [
            "tests/fixtures/dg_everest/everest_0430_R1C1.tiny.tif",
            output,
            "--ndv",
            "[0, 0, 0]",
            "--co",
            "blockxsize=128",
            "--co",
            "blockysize=128",
        ],
    )
    assert result.exit_code == 0
    assert os.path.exists(output)
    with rasterio.open(output) as out:
        assert out.count == 4
        assert out.dtypes[-1] == rasterio.uint8
        assert out.dtypes[0] == rasterio.uint8
        assert out.profile["tiled"] is False
        assert int(out.profile["blockxsize"]) == 128
        assert int(out.profile["blockysize"]) == 128


def test_cli_creation_opts(tmpdir):
    output = str(tmpdir.join("test_alpha_opts.tif"))
    runner = CliRunner()
    result = runner.invoke(
        alpha,
        [
            "tests/fixtures/dg_everest/everest_0430_R1C1.tiny.tif",
            output,
            "--co",
            "compress=lzw",
        ],
    )
    assert result.exit_code == 0

    with rasterio.open(output, "r") as src:
        assert src.compression == Compression.lzw


def test_cli_rgba(tmpdir):
    output = str(tmpdir.join("test_out.tif"))
    runner = CliRunner()
    result = runner.invoke(
        alpha, ["tests/fixtures/landsat/LC80460272013104LGN01_l8sr.tif", output]
    )
    assert result.exit_code == 0


def test_cli_rgba_ndv(tmpdir):
    output = str(tmpdir.join("test_out.tif"))
    runner = CliRunner()
    result = runner.invoke(
        alpha,
        ["--ndv", "0", "tests/fixtures/landsat/LC80460272013104LGN01_l8sr.tif", output],
    )
    assert result.exit_code == 0


def test_cli_equivalent_masks(tmpdir):
    out1 = str(tmpdir.join("internal-to-rgba.tif"))
    runner = CliRunner()
    result = runner.invoke(alpha, ["tests/fixtures/masks/internal_mask.tif", out1])
    assert result.exit_code == 0

    out2 = str(tmpdir.join("external-to-rgba.tif"))
    runner = CliRunner()
    result = runner.invoke(alpha, ["tests/fixtures/masks/external_mask.tif", out2])
    assert result.exit_code == 0

    with rasterio.open(out1) as src1, rasterio.open(out2) as src2:
        assert np.array_equal(src1.read(4), src2.read(4))


def test_cli_must_be_3or4band(tmpdir):
    output = str(tmpdir.join("test_out.tif"))
    runner = CliRunner()
    result = runner.invoke(alpha, ["tests/fixtures/landsat/two_bands.tif", output])
    assert result.exit_code != 0
    assert "Array must have 3 or 4 bands (RGB or RGBA)" in result.output
