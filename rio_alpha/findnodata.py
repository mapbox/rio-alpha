#!/usr/bin/env python
import argparse, math, sys, warnings
import numpy as np
import numpy.ma as ma
import pprint
import rasterio as rio
from rasterio import features
from rasterio.features import sieve
import scipy as sp
from scipy.stats import itemfreq
from scipy.stats import *
from scipy.stats import mode
from os.path import isfile
from utils import (
    _convert_rgb, _group,
    _mode_response, _find_continuous_rgb)


def discover_ndv(rgb_orig, debug):
    rgb_mod, rgb_mod_flat = _convert_rgb(rgb_orig)
    # Full image mode bincount
    mode_vals = stats.mode(rgb_mod_flat)
    candidate_original = []

    for i in range(3):
        candidate = int((mode_vals[0])[0, i]) # modal rgb value from full image
        candidate_original.append(candidate)

    # Find continuous values in RGB array
    candidate_continuous = _compute_continuous(rgb_mod, 1)
 
    # If debug mode, print histograms & be verbose
    if debug:
        _debug_mode(rgb_mod_flat, candidate_original, candidate_continuous)

    # Compare ndv candidates from full & squished image
    candidate_list = [i for i, j in zip(candidate_original, candidate_continuous) if i == j]

    # If candidates from original & filtered images match exactly, print value & exit
    if len(candidate_list) == 3:
        click.echo ('{} {} {}'.format(*candidate_list))

    # If candidates do not match exactly, continue vetting process
    # by searching image edge for frequency of each candidate
    elif len(candidate_list) < 3:
        if debug:
            click.echo("Competing ndv candidates...searching "
                       "image collar for value frequency")

        # Make array of image edge
        top_row = rgb_mod[0,:,:]
        bottom_row = rgb_mod[-1,:,:]
        first_col = rgb_mod[:,0,:]
        last_col = rgb_mod[:,-1,:]
        img_edge = np.concatenate(
                        (top_row,last_col, bottom_row, first_col),
                        axis=0
                    )

        # Squish image edge down to just continuous values 
        edge_mode_continuous = _compute_continuous(rgb_mod, 0)

        # Empty lists for full image edge & squished image edge frequency count
        count_img_edge_full = []
        count_img_edge_continuous = []

        for candidate in (candidate_original, candidate_continuous):

            # Count nodata value frequency in full image edge & squished image edge
            nodata = np.transpose(np.where((img_edge == candidate).all(axis = 1))) 
            count_img_edge_full.append(len(nodata))
            nodata_continuous = np.transpose(np.where((a == candidate).all(axis = 1))) 
            count_img_edge_continuous.append(len(nodata_continuous))

            if debug:
                click.echo('Candidate value: %s '
                           'Candidate count: %s '
                           'Continuous count: %s'
                           % (str(candidate), str(len(nodata)),
                              str(len(nodata_continuous))))

        # Q: will these always realiably be ordered as listed above with original first, continuous second?
        if (count_img_edge_full[0] > count_img_edge_full[1]) and \
           (count_img_edge_continuous[0] > count_img_edge_continuous[1]):
            _mode_response("Detected ndv: ", candidate_original)

        elif (count_img_edge_full[0] < count_img_edge_full[1]) and \
             (count_img_edge_continuous[0] < count_img_edge_continuous[1]):
            _mode_response("Detected ndv: ", candidate_continuous)

        else:
            if debug:
                click.eho('None')
            else:
                click.echo('')
    else:
        click.echo('Invalid %s ' % (str(candidate_list)))



def determine_nodata(src_path, debug, discovery):
    # """returns a 2D array with a GDAL-style mask determined by
    # the following criteria, in order of precedence:

    # 1. If a .msk file, dataset-wide alpha or internal mask exists,
    #    it will be used as the dataset mask.
    # 2. If a 4-band RGBA with a shadow nodata value,
    #    band 4 will be used as the dataset mask.
    # 3. If a nodata value exists, use the binary OR (|) of the band masks
    # 4. If no nodata value exists, return a mask filled with all valid data (255)
    # 5. User supplies the nodata value, input a single value or
    #    a list of per-band values. Default is None.

    # Parameters
    # ----------
    # src_path: string
    # user_nodata: single value (int|float) or list of per-band values.
    #              [Default: None]

    # Returns
    # -------
    # alpha: ndarray, 2D with shape == (2, height, width)

    # """
    # with rio.open(src_path) as src:
    #     if user_nodata:
    #         alpha = get_alpha_mask(...., nodata=user_nodata)
    #     else:
    #         alpha = src.dataset_mask()

    # return alpha

#!/usr/bin/env python

### TAKES INPUT FILE AND REPORTS NO DATA VALUE BASED ON:
###  1) reports "alpha" if alpha channel exists
###  2) internal ndv if one exists exists
###  3) if neither 1 or 2, try mapbox written disovery method (discover_ndv function)

## Current pxm-alpha script:
  with rio.open(src_path, "r") as src:
    count = src.count
    data = src.read()
    if (count == 4 ):
        click.echo("alpha")
    else:
        nodata = src.nodata
        if (nodata == None):
            if discovery:
                discover_ndv(data)
            else:
                print ""
        else:
            click.echo('%s %s %s' % (str(int(nodata)),
                                     str(int(nodata)),
                                     str(int(nodata))))


