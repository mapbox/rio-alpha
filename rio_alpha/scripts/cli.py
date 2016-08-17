import click
import rasterio as rio
from rio_alpha.utils import _parse_ndv
from rio_alpha.islossy import count_ndv_regions
from rio_alpha.findnodata import determine_nodata




logger = logging.getLogger('rio_alpha')


@click.group('alpha')
def toa():
    """Add alpha band to imagery based on nodata values,
        Find nodata in input image.
    """
    pass


@click.command('islossy')
@click.argument('input', nargs=1, type=click.Path(exists=True))
@click.option('--ndv', default='[0, 0, 0]')
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
@click.argument('src_path', type=click.Path(exists=True), help="Input raster")
@click.options('--user_nodata', '-u', default=None,
               help='User supplies the nodata value, '\
                'input a single value or a list of per-band values.' 
               )
@click.options('--debug', help='Enables matplotlib & printing of figures')
@click.options('--verbose',
                help='Prints extra information, '\
                'like competing candidate values')
@click.options('--discovery',
                help='Prints extra information,'\
                ' like competing candidate values'))
def findnodata(src_path, user_nodata, debug, verbose, discovery):

    determine_nodata(src_path, user_nodata)

with rio.drivers():
  with rio.open(args.infile, "r") as src:
    count = src.count

if ( count == 4 ):
    print "alpha"
else:
    nodata = src.nodata
    if ( nodata == None ):
        if args.discovery:
            discover_ndv()
        else:
            print ""
    else:
        print str(int(nodata)) + " " + str(int(nodata)) + " " + str(int(nodata))


alpha.add_command(islossy)
alpha.add_command(findnodata)
