from __future__ import division
import json
import math
import re

import numpy as np
from scipy.stats import mode


def _parse_single(n):
    """Returns a single value nodata of type float

    Parameters
    ----------
    n: integer or str(integer)

    Returns
    -------
    float(n)

    """
    try:
        return float(n)
    except ValueError:
        raise ValueError('{0} is not a valid nodata value'.format(n))


def _parse_ndv(ndv, bands):
    """Returns a list of nodata values of type float

    Parameters
    ----------
    ndv: string, str(list of nodata values)
    bands: integer, band count

    Returns
    -------
    list: list of floats, length = band count

    """

    if re.match(r'\[[0-9\.\,\s]+\]', ndv):
        ndvals = [_parse_single(n) for n in json.loads(ndv)]
        if len(ndvals) != bands:
            raise ValueError('{0} parsed to ndv of {1} does '
                             'not match band count of {2}'.format(
                              ndv, json.dumps(ndvals), bands
                             ))
        else:
            return ndvals
    else:
        return [_parse_single(ndv) for i in range(bands)]


def _convert_rgb(rgb_orig):
    # Sample to ~200 in smaller dimension if > 200 for performance
    if rgb_orig[:, :, 0].shape[0] < rgb_orig[:, :, 0].shape[1]:
        min_dimension = 0
    else:
        min_dimension = 1

    if rgb_orig[:, :, 0].shape[min_dimension] < 200:
        mod = 1
    else:
        mod = int(math.ceil(rgb_orig[:, :, 0].shape[min_dimension] / 200))

    rgb_mod = rgb_orig[::mod, ::mod]
    # Flatten image for full img histogram
    rgb_mod_flat = rgb_mod.reshape(
                        (rgb_mod.shape[0]*rgb_mod.shape[1],
                         rgb_mod.shape[-1]))

    return rgb_mod, rgb_mod_flat


# Squish array to only continuous values, return is in list form
def _find_continuous_rgb(input_array, axis_num):
    diff_array = np.diff(input_array, axis=int(axis_num))
    diff_array = np.insert(diff_array, 0, [99, 99, 99], axis=int(axis_num))
    val_list = (input_array[diff_array == [0, 0, 0]]).tolist()
    return val_list


# Find modal RGB value of continuous values array
# (val_list), takes list, returns [R,G,B]
def _group(lst, n, continuous):
    arr = np.asarray(list(zip(*[lst[i::n] for i in range(n)])))
    mode_vals = mode(arr)
    continuous = [int((mode_vals[0])[0, i]) for i in range(3)]
    return continuous, arr


def _compute_continuous(rgb_mod, loc):
    cont_lst = []
    return _group(_find_continuous_rgb(rgb_mod, loc),
                  3,
                  cont_lst)


def _search_image_edge(rgb_mod, candidate_original, candidate_continuous):
    # Make array of image edge
    top_row = rgb_mod[0, :, :]
    bottom_row = rgb_mod[-1, :, :]
    first_col = rgb_mod[:, 0, :]
    last_col = rgb_mod[:, -1, :]
    img_edge = np.concatenate(
                    (top_row, last_col, bottom_row, first_col),
                    axis=0
                )

    # Squish image edge down to just continuous values
    edge_mode_continuous, arr = _compute_continuous(rgb_mod, 0)

    # Count nodata value frequency in full image edge & squished image edge
    count_img_edge_full = \
        [len(np.transpose(np.where((img_edge == candidate).all(axis=1))))
            for candidate in (candidate_original, candidate_continuous)]

    count_img_edge_continuous = \
        [len(np.transpose(np.where((arr == candidate).all(axis=1))))
            for candidate in (candidate_original, candidate_continuous)]

    return count_img_edge_full, count_img_edge_continuous


def _evaluate_count(lst1, lst2, verbose):
    # Q: will these always realiably be ordered as listed
    # above with original first, continuous second?
    if (lst1[0] > lst1[1]) and \
       (lst2[0] > lst2[1]):
        return lst1

    elif (lst1[0] < lst1[1]) and \
         (lst2[0] < lst2[1]):
        return lst2

    else:
        if verbose:
            return "None"
        else:
            return ""


def _debug_mode(rgb_flat, arr, output):
    import matplotlib.pyplot as plt
    plt.hist(rgb_flat, bins=range(256))
    # histogram of continuous values only
    plt.hist(arr, bins=range(256))
    plt.savefig(output, bbox_inches='tight')
    plt.close()
