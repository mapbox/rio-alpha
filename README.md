
rio-alpha
=========
[![CircleCI](https://circleci.com/gh/mapbox/rio-alpha/tree/master.svg?style=shield&circle-token=e0e2f1cae4332f0c85e0007d7b8c1b4d02dc0e17)](https://circleci.com/gh/mapbox/rio-alpha) [![codecov](https://codecov.io/gh/mapbox/rio-alpha/branch/master/graph/badge.svg?token=jgKj1UPcpd)](https://codecov.io/gh/mapbox/rio-alpha)

A [rasterio](https://github.com/mapbox/rasterio) plugin for working with nodata. Provides a cli and python modules.


Installation
------------

```bash
pip install git+ssh://git@github.com/mapbox/rio-alpha
```

Alternatively, if you're looking to contibute:

```bash
git clone git@github.com:mapbox/rio-alpha.git
cd rio-alpha
pip install -e ".[test]"
```


Usage
-----

#### `islossy`

```bash
❯ rio islossy --help

Usage: rio islossy [OPTIONS] INPUT

  Determine if there are >= 10 nodata regions in an image

  If true, returns the string `--lossy lossy`.

Options:
  --ndv TEXT  Expects an integer or a len(list) == 3 representing a nodata
              value
```

This is a direct replacement for the `pxm-islossy` function in  [pxm](https://github.com/mapbox/pxm/blob/88f147e91bfaad84f4e1777fc4be4cf9dec1d294/pxm-islossy).


#### `findnodata`

```bash
❯ rio findnodata --help

Usage: rio findnodata [OPTIONS] SRC_PATH

Options:
  -u, --user_nodata TEXT  User supplies the nodata value, input a single value
                          or a string of list containing per-band values.
  --discovery             Determines nodata if alpha channeldoes not exist or
                          internal ndv does not exist
  --debug                 Enables matplotlib & printing of figures
  -v, --verbose           Prints extra information, like competing candidate
                          values
  --help                  Show this message and exit.

```
This is a direct replacement for the `pxm-findnodata` function in  [pxm](https://github.com/mapbox/pxm/blob/88f147e91bfaad84f4e1777fc4be4cf9dec1d294/pxm-findnodata).


#### `alpha`

```bash
❯ rio alpha --help

Usage: rio alpha [OPTIONS] SRC_PATH DST_PATH

Options:
  --ndv TEXT             Expects an integer or a list of 3 integers
                         representing nodata values
  --blocksize INTEGER    block size for interal tiling
  -j, --workers INTEGER
  --co NAME=VALUE        Driver specific creation options.See the
                         documentation for the selected output driver for more
                         information.
  --help                 Show this message and exit.

  This is a direct replacement for `pxm-alpha` function (non-lossy data only) in  [pxm](https://github.com/mapbox/pxm/blob/88f147e91bfaad84f4e1777fc4be4cf9dec1d294/pxm-findnodata).
