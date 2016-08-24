import logging
import click
import rasterio as rio
from rio_alpha.utils import _parse_ndv
from rio_alpha.islossy import count_ndv_regions
from rio_alpha.findnodata import determine_nodata
from rio_alpha.addalpha import add_alpha
from os.path import isfile

logger = logging.getLogger('rio_alpha')


@click.group('alpha')
def alpha():
    '''Nodata utilities
    '''
    pass


@click.command('islossy')
@click.argument('input', nargs=1, type=click.Path(exists=True))
@click.option('--ndv', default='[0, 0, 0]',
              help='Expects an integer or a len(list) '
              '== 3 representing a nodata value')
def islossy(input, ndv):
    """
    Determine if there are >= 10 nodata regions in an image
    If true, returns the string `--lossy lossy`.
    """
    with rio.open(input, "r") as src:
        img = src.read()

    ndv = _parse_ndv(ndv, 3)

    if count_ndv_regions(img, ndv) >= 10:
        click.echo("--lossy lossy")
    else:
        click.echo("")


@click.command('findnodata')
@click.argument('src_path', type=click.Path(exists=True))
@click.option('--user_nodata', '-u',
              default=None,
              help="User supplies the nodata value, "
              "input a single value or a string of list "
              "containing per-band values.")
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


@click.command('addalpha')
@click.argument('src_path', type=click.Path(exists=True))
@click.argument('dst_path', type=click.Path(exists=False))
@click.option('--ndv', default='[0, 0, 0]',
              help='Expects an integer or a len(list) '
              '== 3 representing a nodata value')
@click.option('--lossy', is_flag=True,
              help='treat image for lossyno data values')
@click.option('--threshold', type=int,
              help='Overrides range threshold for lossy pixel value')
@click.option('--sieve_size', type=int,
              help='Overrides sieve size')
@click.option('--blocksize', type=int,
              help='block size for interal tiling')
@click.option('--debug', is_flag=True,
              default=False,
              help="Enables matplotlib & printing of figures")
@click.option('--workers', '-j', type=int, default=4)
def addalpha(src_path, dst_path, ndv, lossy, threshold,
             sieve_size, blocksize, debug, workers):
    ndv = _parse_ndv(ndv, 3)
    add_alpha(src_path, dst_path, ndv, lossy, threshold,
              sieve_size, blocksize, debug, workers)


alpha.add_command(islossy)
alpha.add_command(findnodata)
alpha.add_command(addalpha)
