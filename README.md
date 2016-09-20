
rio-alpha
=========

[![Build Status](https://travis-ci.org/mapbox/rio-alpha.svg?branch=master)](https://travis-ci.org/mapbox/rio-alpha)
[![Coverage Status](https://coveralls.io/repos/github/mapbox/rio-alpha/badge.svg?branch=master)](https://coveralls.io/github/mapbox/rio-alpha?branch=master)


A [rasterio](https://github.com/mapbox/rasterio) plugin for working with nodata. Provides a cli and python modules.


Installation
------------

```
pip install -U pip
pip install rio-alpha
```

Alternatively, if you're looking to contribute:

```
git clone git@github.com:mapbox/rio-alpha.git
cd rio-alpha
pip install -U pip
pip install -r requirements.txt
pip install -e .
```


Usage
-----

#### `alpha`

```
❯ rio alpha --help

Usage: rio alpha [OPTIONS] SRC_PATH DST_PATH

Options:
  --ndv TEXT             Expects a string containing a single integer value
                         (e.g. '255') or a string representation of a list
                         containing per-band nodata values (e.g. '[255, 255,
                         255]').
  -j, --workers INTEGER
  --co NAME=VALUE        Driver specific creation options.See the
                         documentation for the selected output driver for more
                         information.
  --help                 Show this message and exit.
```

#### `islossy`

```
❯ rio islossy --help

Usage: rio islossy [OPTIONS] INPUT

  Determine if there are >= 10 nodata regions in an image

  If true, returns the string `True`. If false, returns the string 'False'

Options:
  --ndv TEXT  Expects a string containing a single integer value (e.g. '255')
              or a string representation of a list containing per-band nodata
              values (e.g. '[255, 255, 255]').
  --help      Show this message and exit.
```


#### `findnodata`

```
❯ rio findnodata --help

Usage: rio findnodata [OPTIONS] SRC_PATH

Options:
  -u, --user_nodata TEXT  User supplies the nodata value, input a string
                          containing a single integer value (e.g. '255') or a
                          string representation of a list containing per-band
                          nodata values (e.g. '[255, 255, 255]').
  --discovery             Determines nodata if alpha channeldoes not exist or
                          internal ndv does not exist
  --debug                 Enables matplotlib & printing of figures
  -v, --verbose           Prints extra information, like competing candidate
                          values
  --help                  Show this message and exit.

```
