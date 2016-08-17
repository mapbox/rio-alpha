import click
import numpy as np
import skimage
from skimage import measure


def check(ndv, rgb):
    np.set_printoptions(threshold=np.nan)

    # Discover unique labels to count ndv regions
    label_img = np.invert(np.all(np.rollaxis(rgb, 0, 3) == (ndv), axis=2)).astype(rgb.dtype) * np.iinfo(rgb.dtype).max

    # TODO: neighbors is deprecated, use `connectivity` instead.
    label_array, n_labels = skimage.measure.label(label_img, background=255, neighbors=4, return_num=True)

    return n_labels
