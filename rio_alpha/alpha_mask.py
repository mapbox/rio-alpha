import numpy as np


def rgb_to_rgba(img, ndv, mode='exact'):
    depth, rows, cols = img.shape
    method_map = {
        'exact': mask_exact
    }

    if not mode in method_map:
        raise ValueError()

    alpha = method_map[mode](img, ndv)

    return np.append(img,
                    alpha.reshape(1, rows, cols),
                    axis=0
                     )

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
        ndarray mask of shape (rows, cols) where opaque == 0 and transparent == max of dtype
    '''
    depth, rows, cols = img.shape
    nd = np.iinfo(img.dtype).max
    alpha = np.invert(np.all(np.rollaxis(img, 0, depth) == ndv, axis=2)).astype(img.dtype) * nd

    return alpha