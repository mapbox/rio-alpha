import numpy as np
from skimage import measure


def _mask_exact(img, ndv):
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
    depth, _, _ = img.shape
    nd = np.iinfo(img.dtype).max

    return np.invert(np.all(np.rollaxis(img, 0, depth) == (ndv), axis=2)).astype(img.dtype) * nd


def count_ndv_regions(ndv, rgb):
    """
    Discover unique labels to count ndv regions.
    """
    np.set_printoptions(threshold=np.nan)

    img = _mask_exact(ndv, rgb)

    _, n_labels = measure.label(
        img,
        background=255,
        neighbors=4,
        return_num=True
    )

    return n_labels
