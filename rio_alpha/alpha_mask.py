import numpy as np


def mask_exact(img, ndv):
    '''Exact nodata masking based on ndv

    Parameters
    -----------
    img: ndarray
        (depth x rows x cols) array
    ndv: (list|tuple|ndarray)
        list of notdata values where len == img depth

    Returns
    --------
    alpha: ndarray
        ndarray mask of shape (rows, cols) where
        opaque == 0 and transparent == max of dtype
    '''
    depth, rows, cols = img.shape
    alpha = np.any(np.rollaxis(img, 0, depth) != ndv, axis=2)
    alpha_rescale = alpha.astype(img.dtype) * np.iinfo(img.dtype).max

    return alpha_rescale
