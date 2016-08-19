import re
import json


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
        mod = math.ceil(rgb_orig[:, :, 0].shape[min_dimension] / 200)

    rgb_mod = rgb_orig[::mod, ::mod]
    # Flatten image for full img histogram
    rgb_mod_flat = rgb_mod.reshape(
                        (rgb_mod.shape[0]*rgb_mod.shape[1],
                         rgb_mod.shape[-1]))

    return rgb_mod, rgb_mod_flat


# Squish array to only continuous values, return is in list form
def _find_continuous_rgb(input_array, axis_num):
    diff_array = np.diff(input_array, axis=int(axis_num))
    diff_array = np.insert(diff_array,0,[99, 99, 99], axis=int(axis_num))
    val_list = (input_array[diff_array == [0, 0, 0]]).tolist()
    return val_list


# Find modal RGB value of continuous values array (val_list), takes list, returns [R,G,B]
def _group(lst, n, continuous):
    a = np.asarray(zip(*[lst[i::n] for i in range(n)]))
    mode_vals = stats.mode(a)
    for i in range(3):
        candidate_modal = int((mode_vals[0])[0,i])
        continuous.append(candidate_modal)
    return continuous


def _compute_continous(rgb_mod, loc):
    val_lst = _find_continuous_rgb(rgb_mod, loc) # IDs location of continuousvalues, returns "val_list"
    cont_lst= []
    return _group(val_list, 3, cont_lst) # Converts continuous indexes back to RGB values


def _mode_response(text, winner):
    if debug:
        click.echo('%s %s' % (str(text) + str(winner)))
    else:
        click.echo('{} {} {}'.format(*winner))

def _debug_mode(rgb_flat, candidate_original, candidate_continuous):
    import matplotlib.pyplot as plt
    plt.hist(rgb_flat, bins=range(256))
    plt.show()
    plt.hist(a, bins=range(256)) #histogram of continuous values only
    plt.show()
    click,echo('Original image ndv candidate: %s' %(str(candidate_original)))
    click.echo('Filtered image ndv candidate: %s' %(str(candidate_continuous)))
