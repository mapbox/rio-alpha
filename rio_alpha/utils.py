import re
import json


def _parse_single(n):
    try:
        return float(n)
    except ValueError:
        raise ValueError('{0} is not a valid nodata value'.format(n))


def _parse_ndv(ndv, bands):
    if re.match(r'\[[0-9\.\,\s]+\]', ndv):
        ndvals = [_parse_single(n) for n in json.loads(ndv)]
        if len(ndvals) != bands:
            raise ValueError('{0} parsed to ndv of {1} does not match band count of {2}'.format(
                ndv, json.dumps(ndvals), bands
                ))
        else:
            return ndvals
    else:
        return [_parse_single(ndv) for i in range(bands)]
