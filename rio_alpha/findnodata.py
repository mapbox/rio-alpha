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


def determine_nodata(src_path, user_nodata):
"""returns a 2D array with a GDAL-style mask determined by
the following criteria, in order of precedence:

1. If a .msk file, dataset-wide alpha or internal mask exists,
   it will be used as the dataset mask.
2. If a 4-band RGBA with a shadow nodata value,
   band 4 will be used as the dataset mask.
3. If a nodata value exists, use the binary OR (|) of the band masks
4. If no nodata value exists, return a mask filled with all valid data (255)
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

"""
    with rio.open(src_path) as src:
        if user_nodata:
            alpha = get_alpha_mask(..., nodata=user_nodata)
        else:
            alpha = src.dataset_mask()

    return alpha



### Current pxm-alpha script:

### TAKES INPUT FILE AND REPORTS NO DATA VALUE BASED ON:
###  1) reports "alpha" if alpha channel exists
###  2) internal ndv if one exists exists
###  3) if neither 1 or 2, try mapbox written disovery method (discover_ndv function)

# # Squish array to only continuous values, return is in list form
# def find_continuous_rgb(input_array, axis_num):
#     global val_list
#     diff_array = np.diff(input_array, axis=int(axis_num))
#     diff_array = np.insert(diff_array,0,[99, 99, 99], axis=int(axis_num))
#     val_list = (input_array[diff_array == [0, 0, 0]]).tolist()
#     return val_list

# # Find modal RGB value of continuous values array (val_list), takes list, returns [R,G,B]
# def group(lst, n, continuous):
#     global a
#     a = np.asarray(zip(*[lst[i::n] for i in range(n)])) # 
#     mode_vals = stats.mode(a)
#     for i in range(3):
#         candidate_modal = int((mode_vals[0])[0,i]) 
#         continuous.append(candidate_modal)
#     return continuous

# def mode_response(text, winner):
#     if args.debug:
#         print str(text) + str(winner)
#     else:
#         print '{} {} {}'.format(*winner)

# def debug_mode(rgb_flat, candidate_original, candidate_continuous):
#     if args.debug:
#         import matplotlib.pyplot as plt
#         plt.hist(rgb_flat, bins=range(256))
#         plt.show()
#         plt.hist(a, bins=range(256)) #histogram of continuous values only
#         plt.show()
#         print "Original image ndv candidate:" + str(candidate_original)
#         print "Filtered image ndv candidate:" + str(candidate_continuous)
#     else:
#         None

# def discover_ndv(): 
#     with rio.drivers():
#         with rio.open(args.infile, "r") as src:
#             rgb_orig = np.rollaxis(src.read(), 0, 3)
#     # Sample to ~200 in smaller dimension if > 200 for performance
#     min_dimension = 0 if rgb_orig[:,:,0].shape[0] < rgb_orig[:,:,0].shape[1] else 1;
#     mod = 1 if rgb_orig[:,:,0].shape[min_dimension] < 200 else math.ceil(rgb_orig[:,:,0].shape[min_dimension] / 200)

#     rgb_mod = rgb_orig[::mod, ::mod]
#     # Flatten image for full img histogram
#     rgb_mod_flat = rgb_mod.reshape((rgb_mod.shape[0]*rgb_mod.shape[1], rgb_mod.shape[-1]))


#     # Full image mode bincount
#     mode_vals = stats.mode(rgb_mod_flat)
#     candidate_original = []

#     for i in range(3):
#         candidate = int((mode_vals[0])[0,i]) # modal rgb value from full image
#         candidate_original.append(candidate)

#     # Find continuous values in RGB array
#     find_continuous_rgb(rgb_mod, 1) # IDs location of continuous values, returns "val_list"
#     candidate_continuous = []
#     group(val_list, 3, candidate_continuous) # Converts continuous indexes back to RGB values

#     # If debug mode, print histograms & be verbose
#     debug_mode(rgb_mod_flat, candidate_original, candidate_continuous)

#     # Compare ndv candidates from full & squished image
#     candidate_list = [i for i, j in zip(candidate_original, candidate_continuous) if i == j]

#     # If candidates from original & filtered images match exactly, print value & exit
#     if len(candidate_list) == 3:
#         print '{} {} {}'.format(*candidate_list)

#     # If candidates do not match exactly, continue vetting process by searching image edge for frequency of each candidate
#     elif len(candidate_list) < 3:
#         if args.debug:
#             print "Competing ndv candidates...searching image collar for value frequency"

#         # Make array of image edge
#         top_row = rgb_mod[0,:,:]
#         bottom_row = rgb_mod[-1,:,:]
#         first_col = rgb_mod[:,0,:]
#         last_col = rgb_mod[:,-1,:]
#         img_edge = np.concatenate((top_row,last_col, bottom_row, first_col), axis=0)

#         # Squish image edge down to just continuous values 
#         find_continuous_rgb(img_edge, 0)
#         edge_mode_continuous = []
#         group(val_list, 3, edge_mode_continuous) # gives back "edge_mode_continuous" (mode of cont array) & "a" which is searched for freq of each candidate below

#         # Empty lists for full image edge & squished image edge frequency count
#         count_img_edge_full = []
#         count_img_edge_continuous = []

#         for candidate in (candidate_original, candidate_continuous):

#             # Count nodata value frequency in full image edge & squished image edge
#             nodata = np.transpose(np.where((img_edge == candidate).all(axis = 1))) 
#             count_img_edge_full.append(len(nodata))
#             nodata_continuous = np.transpose(np.where((a == candidate).all(axis = 1))) 
#             count_img_edge_continuous.append(len(nodata_continuous))

#             if args.debug:
#                 print "Candidate value: " + str(candidate) + "  Candidate count: " + str(len(nodata)) + "  Continuous count: " + str(len(nodata_continuous))

#         # Q: will these always realiably be ordered as listed above with original first, continuous second?
#         if ( count_img_edge_full[0] > count_img_edge_full[1] ) and ( count_img_edge_continuous[0] > count_img_edge_continuous[1] ):
#             mode_response("Detected ndv: ", candidate_original)

#         elif ( count_img_edge_full[0] < count_img_edge_full[1] ) and ( count_img_edge_continuous[0] < count_img_edge_continuous[1] ):
#             mode_response("Detected ndv: ", candidate_continuous)

#         else:
#             if args.debug:
#                 print "None"
#             else:
#                 print ""
#     else:
#         print "Invalid" + str(candidate_list)
#         exit()



