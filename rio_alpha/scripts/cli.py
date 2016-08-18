import click
import rasterio as rio

from rio_alpha.islossy import count_ndv_regions
from rio_alpha.utils import _parse_ndv


@click.group('alpha')
def alpha():
    '''Nodata utilities
    '''
    pass


@click.command('islossy')
@click.argument('input', nargs=1, type=click.Path(exists=True))
@click.option('--ndv', default='[0, 0, 0]',
              help='Expects an integer or a len(list) == 3 representing a nodata value')
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


alpha.add_command(islossy)
