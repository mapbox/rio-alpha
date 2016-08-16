import click
import rasterio as rio

from rio_alpha.islossy import check


@click.command('islossy')
@click.argument('ndv', nargs=-1, type=str, required=True)
@click.argument('input', nargs=1, required=True)
def islossy(ndv, input):
    """
    Find nodata in input image
    """
    with rio.open(input, "r") as src:
        rgb = src.read()

    if check(ndv, rgb) >= 10:
        click.echo("--lossy lossy")
    else:
        click.echo("")
