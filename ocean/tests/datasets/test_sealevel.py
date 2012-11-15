#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import os
import urllib
import datetime

import pytest

from ocean.datasets.sealevel import Dataset
from ocean.datasets import ValidationError
from ocean.tests import util

def test_validate_tid():
    qs = urllib.urlencode({
        'dataset': 'sealevel',
        'variable': 'gauge',
        'plot': 'ts',
        'tidalGaugeId': 'IDO70062',
        'period': 'monthly',
    })

    os.environ['QUERY_STRING'] = qs

    params = Dataset.parse()

    print params

def test_validate_tid_bad():
    qs = urllib.urlencode({
        'dataset': 'sealevel',
        'variable': 'gauge',
        'plot': 'ts',
        'tidalGaugeId': 'NOTATID', # bad value
        'period': 'monthly',
    })

    os.environ['QUERY_STRING'] = qs

    with pytest.raises(ValidationError):
        Dataset.parse()

def test_gauge_ts(report):
    util.clear_cache('SEA')

    params = {
        'variable': 'gauge',
        'plot': 'ts',
        'period': 'monthly',
        'tidalGaugeId': 'IDO70062',
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert 'error' not in r
    assert 'tidimg' in r
    assert len(r) == 2

    report.report(params, r['tidimg'])

def test_surface_alt(report):
    util.clear_cache('SEA')

    params = {
        'variable': 'alt',
        'plot': 'map',
        'period': 'monthly',
        'date': datetime.date(2000, 2, 1),
        'area': 'pac',
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert 'error' not in r
    assert 'img' in r
    assert 'altimg' not in r

    assert 'alt' in r['img']

    report.report(params, r['img'])

def test_alt_ts(report):
    util.clear_cache('SEA')

    params = {
        'variable': 'alt',
        'plot': 'ts',
        'period': 'monthly',
        'lat': -30.,
        'lon': 160.,
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert 'error' not in r
    assert 'img' not in r
    assert 'altimg' in r

    assert 'alt' in r['altimg']

    report.report(params, r['altimg'])

def test_surface_rec(report):
    util.clear_cache('SEA')

    params = {
        'variable': 'rec',
        'plot': 'map',
        'period': 'monthly',
        'date': datetime.date(1950, 2, 1),
        'area': 'pac',
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert 'error' not in r
    assert 'img' in r
    assert 'recimg' not in r

    assert 'rec' in r['img']

    report.report(params, r['img'])

def test_rec_ts(report):
    util.clear_cache('SEA')

    params = {
        'variable': 'rec',
        'plot': 'ts',
        'period': 'monthly',
        'lat': -30.,
        'lon': 160.,
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert 'error' not in r
    assert 'img' not in r
    assert 'recimg' in r

    assert 'rec' in r['recimg']

    report.report(params, r['recimg'])
