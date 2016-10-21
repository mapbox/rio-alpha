import click
import numpy as np
import rasterio as rio
from scipy.stats import mode

from rio_alpha.utils import (
    _convert_rgb, _compute_continuous,
    _debug_mode, _search_image_edge, _evaluate_count)


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
    """

    with rio.open(src_path, "r") as src:
        count = src.count
        data = np.rollaxis(src.read(), 0, 3)

    if user_nodata:
        return user_nodata

    if count == 4:
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
