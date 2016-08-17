import numpy as np
from skimage import measure


def _label(ndv, rgb):
    """
    """
    return np.invert(np.all(np.rollaxis(rgb, 0, 3) == (ndv), axis=2)).astype(rgb.dtype) * np.iinfo(rgb.dtype).max


def count_ndv_regions(ndv, rgb):
    """
    Discover unique labels to count ndv regions.
    """
    np.set_printoptions(threshold=np.nan)

    img = _label(ndv, rgb)

    _, n_labels = measure.label(
        img,
        background=255,
        neighbors=4,
        return_num=True
    )

    return n_labels
