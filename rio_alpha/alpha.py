import numpy as np
import rasterio as rio
import riomucho
from rio_alpha.alpha_mask import mask_exact


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
    src = open_file[0]

    arr = src.read(window=window)

    # Determine Alpha Band
    if g_args['ndv']:
        # User-supplied nodata value
        alpha = mask_exact(arr, g_args['ndv'])
    else:
        # Let rasterio decide
        alpha = src.dataset_mask(window=window)

    # Replace or Add alpha band to input data
    if arr.shape[0] == 4:
        # replace band 4 with new alpha mask
        # (likely the same but let's not make that assumption)
        rgba = arr.copy()
        rgba[3] = alpha
    elif arr.shape[0] == 3:
        # stack the alpha mask to add band 4
        rgba = np.append(arr, alpha[np.newaxis, :, :], axis=0)
    else:
        raise ValueError("Array must have 3 or 4 bands (RGB or RGBA)")

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

    dst_profile.update(**creation_options)

    dst_profile.pop('photometric', None)

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
