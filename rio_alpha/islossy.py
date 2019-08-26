"""Evaluate datasets for lossy compression affected nodata masks"""

from rasterio.features import shapes

from rio_alpha.alpha_mask import mask_exact


def count_ndv_regions(img, ndv):
    """Discover unique labels to count ndv regions.

    Parameters
    ----------
    ndv: list
        a list of floats whose length = band count
    img: ndarray
        (depth x rows x cols) array

    Returns
    -------
    int
        The number of connected regions
    """
    img = mask_exact(img, ndv)
    return len(list(shapes(img, mask=(img != 255))))
