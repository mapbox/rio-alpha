import click
import json
import rasterio as rio

from rio_alpha.islossy import count_ndv_regions


@click.command('islossy')
@click.argument('input', nargs=1, type=click.Path(exists=True))
@click.option('--ndv', default='[0, 0, 0]')
def islossy(input, ndv):
    """
    Find nodata in input image
    """
    with rio.open(input, "r") as src:
        rgb = src.read()

    ndv = json.loads(ndv)

    if count_ndv_regions(ndv, rgb) >= 10:
        click.echo("--lossy lossy")
    else:
        click.echo("")
