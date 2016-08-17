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
@click.option('--ndv', default='[0, 0, 0]')
def islossy(input, ndv):
    """
    Find nodata in input image
    """
    with rio.open(input, "r") as src:
        img = src.read()

    ndv = _parse_ndv(ndv, 3)

    if count_ndv_regions(img, ndv) >= 10:
        click.echo("--lossy lossy")
    else:
        click.echo("")


alpha.add_command(islossy)
