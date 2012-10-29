#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import datetime

from ocean.datasets.reynolds import Dataset
from ocean.tests import util

"""
Tests that take the parameter @period will be run for all periods configured
in the Dataset class.
"""

def test_mean(period):
    util.clear_cache('REY')

    params = {
        'area': 'pac',
        'date': datetime.date(2000, 1, 1),
        'period': period,
        'variable': 'mean',
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert not 'error' in r
    assert 'img' in r # FIXME: how do we include this in a test report

def test_anom(period):
    util.clear_cache('REY')

    params = {
        'area': 'pac',
        'date': datetime.date(2000, 1, 1),
        'period': period,
        'variable': 'anom',
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert not 'error' in r
    assert 'img' in r # FIXME: how do we include this in a test report

def test_deciles():
    util.clear_cache('REY')

    params = {
        'area': 'pac',
        'date': datetime.date(2000, 1, 1),
        'period': 'monthly', # FIXME: make test generic
        'variable': 'dec',
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert not 'error' in r
    assert 'img' in r # FIXME: how do we include this in a test report
