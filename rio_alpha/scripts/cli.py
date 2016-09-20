import logging
import click

import rasterio as rio
from rio_alpha.utils import _parse_ndv
from rio_alpha.islossy import count_ndv_regions
from rio_alpha.findnodata import determine_nodata
from rio_alpha.alpha import add_alpha
from rasterio.rio.options import creation_options

logger = logging.getLogger('rio_alpha')


@click.command('islossy')
@click.argument('input', nargs=1, type=click.Path(exists=True))
@click.option('--ndv', default='[0, 0, 0]',
              help="Expects a string containing a single integer value "
              "(e.g. \'255\') or "
              "a string representation of a list containing "
              "per-band nodata values (e.g. \'[255, 255, 255]\').")
def islossy(input, ndv):
    """
    Determine if there are >= 10 nodata regions in an image
    If true, returns the string `--lossy lossy`.
    """
    with rio.open(input, "r") as src:
        img = src.read()

    ndv = _parse_ndv(ndv, 3)

    if count_ndv_regions(img, ndv) >= 10:
        click.echo("True")
    else:
        click.echo("False")


@click.command('findnodata')
@click.argument('src_path', type=click.Path(exists=True))
@click.option('--user-nodata', '-u',
              default=None,
              help="User supplies the nodata value, "
              "input a string containing a single integer value "
              "(e.g. \'255\') or "
              "a string representation of a list containing "
              "per-band nodata values (e.g. \'[255, 255, 255]\').")
@click.option('--discovery', is_flag=True,
              default=False,
              help="Determines nodata if alpha channel"
              "does not exist or internal ndv does not exist")
@click.option('--debug', is_flag=True,
              default=False,
              help="Enables matplotlib & printing of figures")
@click.option('--verbose', '-v', is_flag=True,
              default=False,
              help="Prints extra information, "
              "like competing candidate values")
def findnodata(src_path, user_nodata, discovery, debug, verbose):
    ndv = determine_nodata(src_path, user_nodata, discovery, debug, verbose)
    click.echo("%s" % ndv)


@click.command('alpha')
@click.argument('src_path', type=click.Path(exists=True))
@click.argument('dst_path', type=click.Path(exists=False))
@click.option('--ndv', default='[0, 0, 0]',
              help="Expects a string containing a single integer value "
              "(e.g. \'255\') or "
              "a string representation of a list containing "
              "per-band nodata values (e.g. \'[255, 255, 255]\').")
@click.option('--ndv-masks', is_flag=True,
              default=False,
              help="[Default: False]\n"
                   "The dataset contains one of the following:\n"
                   "1.internal nodata value set in metadata\n"
                   "2.an alpha band\n"
                   "3.an internal binary mask "
                   "(formats like GTiff allow a "
                   "mask that is not considered a band)\n"
                   "4.an external binary mask (a *.msk file alongside "
                   "the main raster)\n")
@click.option('--workers', '-j', type=int, default=1)
@click.pass_context
@creation_options
def alpha(ctx, src_path, dst_path, ndv, ndv_masks, creation_options,
          workers):
    ndv = _parse_ndv(ndv, 3)
    add_alpha(src_path, dst_path, ndv, ndv_masks, creation_options,
              workers)
