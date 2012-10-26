#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import datetime

import ocean
from ocean import util

def test_get_resource():
    p = util.get_resource('maps', 'raster.map')
    assert p.startswith(ocean.__path__[0])
    assert p.endswith('maps/raster.map')

def test_build_response_object():
    o = util.build_response_object(
        ['a', 'b', 'c'],
        'canoe',
        ['.png', '.jpg', '.txt'])

    assert o == {
        'a': 'canoe.png',
        'b': 'canoe.jpg',
        'c': 'canoe.txt',
    }

def test_format_old_date():
    d = datetime.date(1900, 1, 1)
    ds = util.format_old_date(d)

    assert ds == 'January 1900'

    d = datetime.date(2000, 3, 1)
    ds = util.format_old_date(d)

    assert ds == 'March 2000'

    d = datetime.date(1850, 5, 1)
    ds = util.format_old_date(d)

    assert ds == 'May 1850'
