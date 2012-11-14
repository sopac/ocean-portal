#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import time

import pytest
from selenium.common.exceptions import InvalidSelectorException

from ocean.tests import util

from uiutil import *
from test_map import select_region

def test_display_gauges(b, url):
    b.get(url)

    b.select_param('variable', 'Tidal Gauge')
    time.sleep(4) # wait for the map to stabilise
    b.wait(jquery('svg circle'))

    markers = b.find_elements_by_jquery('svg circle')

    print markers

    # check we have the right number of markers
    assert len(markers) == 13

    for m in markers:
        assert m.is_displayed()
        assert m.get_attribute('stroke') == 'white'
        assert m.get_attribute('fill') == 'black'

def test_click_gauge(b, url):
    b.get(url)

    b.select_param('variable', 'Tidal Gauge')
    time.sleep(4) # wait for the map to stabilise
    b.wait(jquery('svg circle'))

    marker = b.find_element_by_jquery('svg circle:first')

    assert marker.get_attribute('stroke') == 'white'

    marker.click()

    assert marker.get_attribute('stroke') == 'red'

    # this will be the first value in the config file
    input = b.find_element_by_id('tidalgauge')
    assert input.get_attribute('value') == "Fiji - Suva"

    input = b.find_element_by_id('tgId')
    assert input.get_attribute('value') == 'IDO70063'

    util.clear_cache('SEA')
    b.submit()
    b.wait(output('SEA'))

def test_gauge_offscreen(b, url):
    b.get(url)

    b.select_param('variable', 'Tidal Gauge')
    select_region(b, 'niue')

    with pytest.raises(InvalidSelectorException):
        # with all the circles offscreen there's nothing to select
        b.find_element_by_jquery('svg circle')

    select_region(b, 'samoa')
    assert len(b.find_elements_by_jquery('svg circle')) > 0
