
rio-alpha
=========
[![CircleCI](https://circleci.com/gh/mapbox/rio-alpha/tree/master.svg?style=shield&circle-token=e0e2f1cae4332f0c85e0007d7b8c1b4d02dc0e17)](https://circleci.com/gh/mapbox/rio-alpha) [![codecov](https://codecov.io/gh/mapbox/rio-alpha/branch/master/graph/badge.svg?token=jgKj1UPcpd)](https://codecov.io/gh/mapbox/rio-alpha)

A [rasterio](https://github.com/mapbox/rasterio) plugin for working with nodata. Provides a cli and python modules.


Installation
------------

```bash
pip install git+ssh://git@github.com/mapbox/rio-alpha
```

Alternatively, if you're looking to contribute:

```bash
git clone git@github.com:mapbox/rio-alpha.git
cd rio-alpha
pip install -e ".[test]"
```


Usage
-----

#### `alpha`

```bash
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

```bash
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

```bash
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
