
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
❯ rio alpha islossy --help                                                                         15:47
Usage: rio alpha islossy [OPTIONS] INPUT

  Determine if there are >= 10 nodata regions in an image

  If true, returns the string `--lossy lossy`.

Options:
  --ndv TEXT  Expects an integer or a len(list) == 3 representing a nodata
              value
```

This is a direct replacement for the `pxm-islossy` function in  [pxm](https://github.com/mapbox/pxm/blob/88f147e91bfaad84f4e1777fc4be4cf9dec1d294/pxm-islossy).

