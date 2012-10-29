#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import datetime

from ocean.datasets.ww3 import Dataset
from ocean.tests import util

"""
Tests that take the parameter @period will be run for all periods configured
in the Dataset class.
"""

def test_plot(variable, period):
    util.clear_cache('WAV')

    params = {
        'date': datetime.date(2000, 1, 1),
        'period': period,
        'variable': variable,
        'lllat': -30.,
        'lllon': 160.,
        'urlat': -30.,
        'urlon': 160.,
    }

    ds = Dataset()
    r = ds.process(params)

    print r

    assert not 'error' in r
    assert 'img' in r # FIXME: how do we include this in a test report
