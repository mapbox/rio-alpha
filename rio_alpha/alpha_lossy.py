import numpy as np
import rasterio as rio
from rasterio.features import sieve
import scipy as sp
from scipy import ndimage
from alpha_mask import mask_exact_threshold, mask_exact
import riomucho


def calc_alpha_thresh(rgb, ndv, thresh):
    lo_list = [(int(item) - thresh) for item in ndv]
    hi_list = [(int(item) + thresh) for item in ndv]

    alpha = mask_exact_threshold(rgb, hi_list, lo_list)

    return alpha


def calc_alpha_eroded(rgb, ndv, thresh, sieveSize, debug):
    alpha = calc_alpha_thresh(rgb, ndv, thresh)
    sieved = sieve(alpha,
                   sieveSize,
                   connectivity=8)
    eroded = sp.ndimage.minimum_filter(sieved, 5)
    eroded[eroded != 255] = 0

    if debug:
        plt.imshow(alpha)
        plt.show()
        plt.imshow(sieved)
        plt.show()

    return eroded


def calc_alpha(rgb, height, width, ndv, thresh, sieve_size, debug):
    if ndv:
        if thresh:
            threshold = int(threshold)
        else:
            # test_gradient = np.diff(rgb, axis=1)
            # pull = int(( np.median(test_gradient) +
            # np.mean(test_gradient) ) / 2)
            threshold = 7

        if sieve_size:
            sieveSize = int(sieve_size)
        else:
            sieveSize = int((height * width) * 0.005)

        eroded = calc_alpha_eroded(rgb, ndv, threshold, sieveSize, debug)

        return eroded

    else:
        alpha = mask_exact(rgb, [0, 0, 0])
        return alpha

    if debug:
        plt.imshow(rgba)
        plt.show()

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
    height, width = rgb.shape[1:]

    alpha = calc_alpha(rgb,
                       height,
                       width,
                       g_args['ndv'],
                       g_args['thresh'],
                       g_args['sieveSize'],
                       g_args['debug'])

    rgba = np.append(rgb, alpha[np.newaxis, :, :], axis=0)

    return rgba


def add_alpha_lossy(src_path, dst_path, ndv, threshold, sieve_size,
              blocksize, debug, processes):

    if debug:
        import matplotlib.pyplot as plt

    with rio.open(src_path) as src:
        dst_profile = src.profile.copy()
        width = src.width
        height = src.height

    if blocksize:
        blocksize = blocksize[0]
    else:
        blocksize = 256

    dst_profile.update(
        count=4,
        transform=dst_profile['affine'],
        nodata=None,
        compress='lzw',
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
        'ndv': ndv,
        'thresh': threshold,
        'sieveSize': sieve_size,
        'debug': debug
    }

    with riomucho.RioMucho([src_path],
                           dst_path,
                           _alpha_worker,
                           options=dst_profile,
                           global_args=global_args,
                           mode='manual_read') as rm:

        rm.run(processes)
