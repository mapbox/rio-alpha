import math
import numpy as np
import numpy.ma as ma
import pprint
import rasterio as rio
import click
from rasterio import features
from rasterio.features import sieve
import scipy as sp
from scipy.stats import mode
from os.path import isfile
from utils import (
    _convert_rgb, _group, _compute_continuous,
    _debug_mode, _find_continuous_rgb,
    _search_image_edge, _evaluate_count)


def discover_ndv(rgb_orig, debug, verbose):
    """Returns nodata value by calculating mode of RGB array

    Parameters
    ----------
    rgb_orig: ndarray
              array of input pixels of shape (rows, cols, depth)
    debug: Boolean
           Enables matplotlib & printing of figures
    verbose: Boolean
             Prints extra information, like competing candidate values


    Returns
    -------
    list of nodata value candidates or empty string if none found

    """
    rgb_mod, rgb_mod_flat = _convert_rgb(rgb_orig)
    # Full image mode bincount
    mode_vals = mode(rgb_mod_flat)
    candidate_original = [int((mode_vals[0])[0, i]) for i in range(3)]

    # Find continuous values in RGB array
    candidate_continuous, arr = _compute_continuous(rgb_mod, 1)

    # If debug mode, print histograms & be verbose
    if debug:
        click.echo('Original image ndv candidate: %s'
                   % (str(candidate_original)))
        click.echo('Filtered image ndv candidate: %s'
                   % (str(candidate_continuous)))
        outplot = "/tmp/hist_plot.png"
        _debug_mode(rgb_mod_flat, arr, outplot)

    # Compare ndv candidates from full & squished image
    candidate_list = [i for i, j in
                      zip(candidate_original, candidate_continuous)
                      if i == j]

    # If candidates from original & filtered images match exactly,
    # print value & exit
    if len(candidate_list) == 3:
        return candidate_list

    # If candidates do not match exactly, continue vetting process
    # by searching image edge for frequency of each candidate
    elif len(candidate_list) < 3:
        if verbose:
            click.echo("Competing ndv candidates...searching "
                       "image collar for value frequency. "
                       "Candidate list: %s" % str(candidate_list))

        count_img_edge_full, count_img_edge_continuous = \
            _search_image_edge(rgb_mod,
                               candidate_original,
                               candidate_continuous)

        if verbose:
            for candidate in (candidate_original, candidate_continuous):
                click.echo('Candidate value: %s '
                           'Candidate count: %s '
                           'Continuous count: %s'
                           % (str(candidate), str(count_img_edge_full),
                              str(count_img_edge_continuous)))

        output = _evaluate_count(count_img_edge_full,
                                 count_img_edge_continuous,
                                 verbose)

        return output

    else:
        return 'Invalid %s ' % (str(candidate_list))


def determine_nodata(src_path, user_nodata, discovery, debug, verbose):
    """Worker function for determining nodata

    Parameters
    ----------
    src_path: string
    user_nodata: string/integer
                 User supplies the nodata value,
                 input a single value or a string of list
    discovery: Boolean
               determines nodata if alpha channel does not exist
               or internal ndv does not exist
    debug: Boolean
           Enables matplotlib & printing of figures
    verbose: Boolean
             Prints extra information, like competing candidate values


    Returns
    -------
    nodata value: string
                  string(int) or stringified array of values of
                  len == the number of bands.
                  For example, string([int(ndv), int(ndv), int(ndv)])


    Current pxm-alpha script:
    TAKES INPUT FILE AND REPORTS NO DATA VALUE BASED ON:
    1. reports "alpha" if alpha channel exists
    2. internal ndv if one exists
    3. if neither 1 or 2, try mapbox written disovery method
       (discover_ndv function)

    New approach returns a 2D array with a GDAL-style mask determined by
    the following criteria, in order of precedence:

    1. If a .msk file, dataset-wide alpha or internal mask exists,
       it will be used as the dataset mask.
    2. If a 4-band RGBA with a shadow nodata value,
       band 4 will be used as the dataset mask.
    3. If a nodata value exists, use the binary OR (|) of the band masks
    4. If no nodata value exists, return a mask filled with all
       valid data (255)
    5. User supplies the nodata value, input a single value or
       a list of per-band values. Default is None.

    Parameters
    ----------
    src_path: string
    user_nodata: single value (int|float) or list of per-band values.
                 [Default: None]

    Returns
    -------
    alpha: ndarray, 2D with shape == (2, height, width)

    # with rio.open(src_path) as src:
    #     if user_nodata:
    #         alpha = get_alpha_mask(...., nodata=user_nodata)
    #     else:
    #         alpha = src.dataset_mask()

    # return alpha

    """

    with rio.open(src_path, "r") as src:
        count = src.count
        data = np.rollaxis(src.read(), 0, 3)

    if user_nodata:
        return user_nodata

    if (count == 4):
        return "alpha"
    else:
        nodata = src.nodata
        if nodata is None:
            if discovery:
                candidates = discover_ndv(data, debug, verbose)
                if len(candidates) != 3:
                    return ""
                else:
                    return '[{}, {}, {}]'.format(*candidates)
            else:
                return ""
        else:
            return '%s' % (str(int(nodata)))
