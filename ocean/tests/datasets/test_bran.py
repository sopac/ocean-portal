#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import datetime

import pytest

from ocean.datasets.bran import Dataset
from ocean.tests import util

"""
Tests that take the parameter @period will be run for all periods configured
in the Dataset class.
"""

def test_surface(report, variable, period):
    util.clear_cache('BRN')

    params = {
        'area': 'fiji',
        'date': datetime.date(2000, 1, 1),
        'period': period,
        'variable': variable,
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert not 'error' in r
    assert 'img' in r

    report(params, r['img'])

@pytest.mark.parametrize(('var'), [
    'temp',
    'salt',
])
def test_salt_xsection(report, var, period):
    util.clear_cache('BRN')

    params = {
        'area': 'pac',
        'date': datetime.date(2000, 1, 1),
        'period': period,
        'variable': var,
        'lat': -30.,
        'lon': 160.,
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert not 'error' in r
    assert 'img' in r

    report(params, r['img'])
