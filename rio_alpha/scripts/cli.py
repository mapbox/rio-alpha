import logging
import click
import rasterio as rio
from rio_alpha.utils import _parse_ndv
from rio_alpha.islossy import count_ndv_regions
from rio_alpha.findnodata import determine_nodata
from os.path import isfile

logger = logging.getLogger('rio_alpha')

@click.group('alpha')
def alpha():
    """Add alpha band to imagery based on nodata values,
        Find nodata in input image.
    """
    pass

@click.command('islossy')
@click.argument('input', nargs=1, type=click.Path(exists=True))
@click.option('--ndv', default=[0, 0, 0])
def islossy(input, ndv):
    """
    Find nodata in input image
    """
    with rio.open(input, "r") as src:
        rgb = src.read()

    ndv = _parse_ndv(ndv, 3)

    if count_ndv_regions(ndv, rgb) >= 10:
        click.echo("--lossy lossy")
    else:
        click.echo("")


@click.command('findnodata')
@click.argument('src_path', type=click.Path(exists=True))
@click.option('--user_nodata', '-u', default=None,
              help="User supplies the nodata value, "
              "input a single value or a list of per-band values.")
@click.option('--debug', help="Enables matplotlib & printing of figures")
@click.option('--verbose', '-v',
              help="Prints extra information, "
              "like competing candidate values")
@click.option('--discovery', default=None,
              help="Prints extra information, "
              "like competing candidate values")
def findnodata(src_path, user_nodata, debug, verbose, discovery):
    # if not isfile(src_path):
    #   click.echo("Could not open file")
    #   pass

    determine_nodata(src_path, user_nodata, discovery)


alpha.add_command(islossy)
alpha.add_command(findnodata)
