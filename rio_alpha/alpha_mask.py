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
    alpha = np.invert(
                    np.all(
                        np.rollaxis(img, 0, depth) == ndv,
                        axis=2))
    alpha_rescale = alpha.astype(img.dtype) * np.iinfo(img.dtype).max

    return alpha_rescale


def mask_exact_threshold(rgb, hi_list, lo_list):
    depth, rows, cols = rgb.shape

    alpha = np.invert(
                np.all(
                    np.rollaxis(
                        np.logical_and(rgb < max(hi_list), rgb > min(lo_list)),
                        0,
                        depth),
                    axis=2))

    alpha_rescale = alpha.astype(rgb.dtype) * np.iinfo(rgb.dtype).max

    return alpha_rescale


# def rgb_to_rgba(img, ndv, mode='exact'):
#     depth, rows, cols = img.shape
#     method_map = {
#         'exact': mask_exact
#     }

#     if not mode in method_map:
#         raise ValueError()

#     alpha = method_map[mode](img, ndv)

#     return np.append(img,
#                     alpha.reshape(1, rows, cols),
#                     axis=0
#                      )
