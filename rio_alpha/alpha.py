import numpy as np
import rasterio as rio
import scipy as sp
from scipy import ndimage
from alpha_mask import mask_exact
import riomucho


def calc_alpha(rgb, ndv):
    """Find nodata in input image

    Add an alpha channel to an image based on one of the following:
    1. no ndv input arg, alpha channel added with 100% 0 vals
    2. --ndv input arg, alpha channel added with where
       opaque == 0 and transparent == max of dtype

    Parameters
    ----------
    rgb: ndarray
         array of input pixels of shape (depth, rows, cols)
    ndv: list
         a list of floats where the
         length of the list = band count

    Returns
    -------
    alpha: ndarray
           ndarray mask of shape (rows, cols) where
           opaque == 0 and transparent == max of dtype

    """
    if ndv:
            alpha = mask_exact(rgb, ndv)
            return alpha

    else:
        alpha = mask_exact(rgb, [0, 0, 0])
        return alpha


def _alpha_worker(open_file, window, ij, g_args):
    """rio mucho worker for alpha. It reads input
    files and perform alpha calculations on each window.

    Parameters
    ------------
    open_files: list of rasterio open files
    window: tuples
            A window is a view onto a rectangular subset of a
            raster dataset and is described in rasterio
            by a pair of range tuples:
            ((row_start, row_stop), (col_start, col_stop))
    g_args: dictionary

    Returns
    ---------
    rgba: ndarray
          ndarray with original RGB bands of shape (3, rows, cols)
          and a mask of shape (rows, cols) where
          opaque == 0 and transparent == max of dtype
    """

    rgb = open_file[0].read(window=window)
    depth, rows, cols = rgb.shape

    alpha = calc_alpha(rgb,
                       g_args['ndv'])

    rgba = np.append(rgb, alpha[np.newaxis, :, :], axis=0)

    return rgba


def add_alpha(src_path, dst_path, ndv, creation_options,
              processes):
    """
    Parameters
    ------------
    src_paths: list of strings
    dst_path: string
    ndv: list
         a list of floats where the
         length of the list = band count
    creation_options: dict
    processes: integer


    Returns
    ---------
    None
        Output is written to dst_path
    """

    with rio.open(src_path) as src:
        dst_profile = src.profile.copy()
        height = src.height
        width = src.width

    dst_profile.update(**creation_options)

    dst_profile.update(
        count=4,
        nodata=None
        )

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
