import numpy as np
from skimage import measure

from rio_alpha.alpha_mask import mask_exact


def count_ndv_regions(ndv, img):
    '''Discover unique labels to count ndv regions.

    Parameters
    ----------
    ndv: list
        a list of floats whose length = band count
    img: ndarray
        (depth x rows x cols) array

    Returns
    -------
    n_labels: int
        an integer equal to the number of connected regions
    '''
    np.set_printoptions(threshold=np.nan)

    img = mask_exact(ndv, img)

    _, n_labels = measure.label(
        img,
        background=255,
        neighbors=4,
        return_num=True
    )

    return n_labels
