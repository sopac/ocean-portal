#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import pytest
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from ocean.tests import util

from uiutil import *

b = None

# --- Fixtures ---

def setup_module(module):
    global b
    b = MapPortalDriver()
    b.set_window_size(1200, 800)

def teardown_module(module):
    b.quit()

# --- Tests ---

@util.requires_display
def test_load(url):
    b.get(url)

    # check Bathymetry is selected and enabled
    elem = b.find_element_by_xpath('//input[@value="Bathymetry"]')
    assert elem.get_attribute('checked')
    assert elem.get_attribute('disabled') is None

    # check Output is unselected and disabled
    elem = b.find_element_by_xpath('//input[@value="Output"]')
    assert elem.get_attribute('checked') is None
    assert elem.get_attribute('disabled')

@util.requires_display
def test_mean_sst_monthly(url):
    b.get(url)

    util.clear_cache('ERA')

    b.select_param('variable', 'Mean Temperature')
    b.ensure_selected('plottype', 'Surface Map', noptions=2)
    b.select_param('period', 'Monthly')
    b.select_param('month', 'January')
    b.select_param('year', '2012')
    b.ensure_selected('dataset', 'ERSST')
    b.submit()

    b.wait(output('ERA'))

    # check Bathymetry is enabled but not selected
    elem = b.find_element_by_xpath('//input[@value="Bathymetry"]')
    assert elem.get_attribute('checked') is None
    assert elem.get_attribute('disabled') is None

    # check Output is enabled and selected
    elem = b.find_element_by_xpath('//input[@value="Output"]')
    assert elem.get_attribute('checked')
    assert elem.get_attribute('disabled') is None

@util.requires_display
def test_wave_watch_rose(url):
    b.get(url)

    util.clear_cache('WAV')

    b.select_param('variable', 'Mean Wave Direction')
    b.ensure_selected('plottype', 'Waverose')
    b.ensure_selected('period', 'Monthly')
    b.select_param('month', 'October') # September and October had a bug
    b.ensure_selected('dataset', 'WaveWatch III')

    elem = b.find_element_by_id('latitude')
    elem.send_keys("-45")
    elem.send_keys(Keys.TAB)

    elem = b.switch_to_active_element()
    elem.send_keys("145")

    b.submit()

    b.wait(output('WAV'))

    # check Bathymetry is selected and enabled
    elem = b.find_element_by_xpath('//input[@value="Bathymetry"]')
    assert elem.get_attribute('checked')
    assert elem.get_attribute('disabled') is None

    # check Output is unselected and disabled
    elem = b.find_element_by_xpath('//input[@value="Output"]')
    assert elem.get_attribute('checked') is None
    assert elem.get_attribute('disabled')

@util.requires_display
def test_removing_outputs(url):
    """
    This test adds a surface output, and then a graph output.

    It then removes the surface output.
    """

    b.get(url)

    # create a surface plot
    b.select_param('variable', 'Mean Temperature')
    b.ensure_selected('plottype', 'Surface Map', noptions=2)
    b.select_param('period', 'Monthly')
    b.select_param('month', 'January')
    b.select_param('year', '2012')
    b.ensure_selected('dataset', 'ERSST')
    b.submit()

    b.wait(output('ERA'))

    # check Bathymetry is enabled but not selected
    elem = b.find_element_by_xpath('//input[@value="Bathymetry"]')
    assert elem.get_attribute('checked') is None
    assert elem.get_attribute('disabled') is None

    # check Output is enabled and selected
    elem = b.find_element_by_xpath('//input[@value="Output"]')
    assert elem.get_attribute('checked')
    assert elem.get_attribute('disabled') is None

    # create a non-surface plot
    b.select_param('variable', 'Mean Wave Direction')
    b.ensure_selected('plottype', 'Waverose')
    b.ensure_selected('period', 'Monthly')
    b.select_param('month', 'October') # September and October had a bug
    b.ensure_selected('dataset', 'WaveWatch III')

    elem = b.find_element_by_id('latitude')
    elem.send_keys("-45")
    elem.send_keys(Keys.TAB)

    elem = b.switch_to_active_element()
    elem.send_keys("145")

    b.submit()

    b.wait(output('WAV'))

    # check Bathymetry is selected and enabled
    elem = b.find_element_by_xpath('//input[@value="Bathymetry"]')
    assert elem.get_attribute('checked')
    assert elem.get_attribute('disabled') is None

    # check Output is unselected but enabled
    elem = b.find_element_by_xpath('//input[@value="Output"]')
    assert elem.get_attribute('checked') is None
    assert elem.get_attribute('disabled') is None

    b.wait(animation_finished)

    # check the # of outputs
    elems = b.find_elements_by_jquery('.outputgroup')
    assert len(elems) == 2

    # delete the 2nd output
    elem = b.find_element_by_jquery('.outputgroup ~ .outputgroup')
    print elem, elem.location
    action = ActionChains(b)
    action.move_to_element(elem)
    action.click(on_element=elem.find_element_by_css_selector('.close-button'))
    action.perform()

    b.wait(animation_finished)

    # check the # of outputs
    elems = b.find_elements_by_jquery('.outputgroup')
    assert len(elems) == 1

    # check Bathymetry is selected and enabled
    elem = b.find_element_by_xpath('//input[@value="Bathymetry"]')
    assert elem.get_attribute('checked')
    assert elem.get_attribute('disabled') is None

    # check Output is unselected and disabled
    elem = b.find_element_by_xpath('//input[@value="Output"]')
    assert elem.get_attribute('checked') is None
    assert elem.get_attribute('disabled')

@util.requires_display
@pytest.mark.parametrize(('variable'), [
    ('Significant Wave Height',),
    ('Mean Wave Period',),
])
def test_histogram(url, variable):
    b.get(url)

    b.select_param('variable', variable)
    b.ensure_selected('plottype', 'Histogram')
    b.select_param('period', 'Monthly')
    b.select_param('month', 'January')

    assert len(b.find_elements_by_jquery('#year:visible')) == 0

    b.ensure_selected('dataset', 'WaveWatch III')

    elem = b.find_element_by_id('latitude')
    elem.send_keys("-45")

    elem = b.find_element_by_id('longitude')
    elem.send_keys("145")

    util.clear_cache('WAV')
    b.submit()
    b.wait(output('WAV'))

@util.requires_display
@pytest.mark.parametrize(('variable', 'dataset', 'product'), [
    ('Mean Temperature', 'Reynolds', 'REY'),
    ('Anomalies', 'Reynolds', 'REY'),
    ('Deciles', 'Reynolds', 'REY'),
    ('Mean Temperature', 'ERSST', 'ERA'),
    ('Anomalies', 'ERSST', 'ERA'),
    ('Deciles', 'ERSST', 'ERA'),
    ('Mean Temperature', 'BRAN', 'BRN'),
    ('Salinity', 'BRAN', 'BRN'),
    ('Reconstruction', 'BRAN', 'BRN'),
    ('Reconstruction', 'Church & White', 'SEA'),
    ('Altimetry', 'Church & White', 'SEA'),
])
def test_surface_maps(url, variable, dataset, product):
    b.get(url)

    b.select_param('variable', variable)
    b.select_param('plottype', 'Surface Map')
    b.select_param('period', 'Monthly')
    b.select_param('year', '2000')
    b.select_param('month', 'November')
    b.select_param('dataset', dataset)

    util.clear_cache(product)
    b.submit()
    b.wait(output(product))

@util.requires_display
@pytest.mark.parametrize(('variable', 'dataset', 'product'), [
    ('Mean Temperature', 'BRAN', 'BRN'),
    ('Salinity', 'BRAN', 'BRN'),
])
def test_cross_sections(url, variable, dataset, product):
    b.get(url)

    b.select_param('variable', variable)
    b.select_param('plottype', 'Sub-surface Cross-section')
    b.select_param('period', 'Monthly')
    b.select_param('year', '2000')
    b.select_param('month', 'November')
    b.select_param('dataset', dataset)

    elem = b.find_element_by_id('latitude')
    elem.send_keys("-45")

    elem = b.find_element_by_id('longitude')
    elem.send_keys("145")

    util.clear_cache(product)
    b.submit()
    b.wait(output(product))

@util.requires_display
def test_currents_bad(url):
    """
    This test will fail because the region is too big.
    """

    b.get(url)

    b.select_param('region', 'Pacific Ocean')
    b.select_param('variable', 'Temp & Currents')
    b.ensure_selected('plottype', 'Surface Map')
    b.ensure_selected('period', 'Monthly')
    b.select_param('month', 'March')
    b.select_param('year', '2005')
    b.ensure_selected('dataset', 'BRAN')

    util.clear_cache('BRN')
    b.submit()

    with pytest.raises(FrontendError):
        b.wait(output('BRN'))

@util.requires_display
@pytest.mark.parametrize(('variable'), [
    ('Temp & Currents',),
    ('Sea Level & Currents',),
])
def test_currents(url, variable):
    b.get(url)

    b.select_param('region', 'Fiji')
    b.select_param('variable', variable)
    b.ensure_selected('plottype', 'Surface Map')
    b.ensure_selected('period', 'Monthly')
    b.select_param('month', 'March')
    b.select_param('year', '2005')
    b.ensure_selected('dataset', 'BRAN')

    util.clear_cache('BRN')
    b.submit()
    b.wait(output('BRN'))
