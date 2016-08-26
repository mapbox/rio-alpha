import numpy as np
import rasterio as rio
import scipy as sp
from scipy import ndimage
from alpha_mask import mask_exact
import riomucho


def calc_alpha(rgb, ndv):
    if ndv:
            alpha = mask_exact(rgb, ndv)
            return alpha

    else:
        alpha = mask_exact(rgb, [0, 0, 0])
        return alpha


def _alpha_worker(open_file, window, ij, g_args):
    """Find nodata in input image

    Add an alpha channel to an image based on one of the following:
    1. no ndv input arg, alpha channel added with 100% 255 vals
    2. --ndv input arg, alpha channel added with 0s at ndv and
       255s elsewhere
    3. add lossy & sieve flags to scenarios with --ndv arg to
       control extent of lossy coverage

    """
    rgb = open_file[0].read(window=window)
    depth, rows, cols = rgb.shape

    alpha = calc_alpha(rgb,
                       g_args['ndv'])

    rgba = np.append(rgb, alpha[np.newaxis, :, :], axis=0)

    return rgba


def add_alpha(src_path, dst_path, ndv, creation_options,
              blocksize, processes):

    with rio.open(src_path) as src:
        dst_profile = src.profile.copy()
        height = src.height
        width = src.width

    dst_profile.update(**creation_options)

    if blocksize:
        blocksize = blocksize
    else:
        blocksize = 256

    dst_profile.update(
        count=4,
        transform=dst_profile['affine'],
        nodata=None,
        tiled=True,
        blockxsize=blocksize,
        blockysize=blocksize
        )

    # workaround for very narrow datasets - don't specify blocksize
    if blocksize > min([width, height]):
        del dst_profile['blockxsize'], dst_profile['blockysize']

    global_args = {
        'src_nodata': 0,
        'dst_dtype': dst_profile['dtype'],
        'ndv': ndv
    }

    with riomucho.RioMucho([src_path],
                           dst_path,
                           _alpha_worker,
                           options=dst_profile,
                           global_args=global_args,
                           mode='manual_read') as rm:

        rm.run(processes)