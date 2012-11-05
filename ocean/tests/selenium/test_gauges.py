#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import pytest
from selenium.common.exceptions import InvalidSelectorException

from ocean.tests import util

from uiutil import *

def test_display_gauges(b, url):
    b.get(url)

    b.select_param('variable', 'Tidal Gauge')
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

def test_gauge_offscreen1(b, url):
    b.get(url)

    b.select_param('region', 'Samoa')
    b.select_param('variable', 'Tidal Gauge')

    with pytest.raises(InvalidSelectorException):
        # with all the circles offscreen there's nothing to select
        b.find_element_by_jquery('svg circle:first')

    b.select_param('region', 'Marshall Islands')
    b.find_element_by_jquery('svg circle:first')

def test_gauge_offscreen2(b, url):
    b.get(url)

    b.select_param('region', 'Samoa')
    b.select_param('variable', 'Tidal Gauge')

    with pytest.raises(InvalidSelectorException):
        # with all the circles offscreen there's nothing to select
        b.find_element_by_jquery('svg circle:first')

    b.select_param('region', 'Fiji')
    b.find_element_by_jquery('svg circle:first')
