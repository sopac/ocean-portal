
from selenium.webdriver.common.keys import Keys

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
def test_load():
    b.get('http://localhost/portal/compmap.html')

    # check Bathymetry is selected and enabled
    elem = b.find_element_by_xpath('//input[@value="Bathymetry"]')
    assert elem.get_attribute('checked')
    assert elem.get_attribute('disabled') is None

    # check Output is unselected and disabled
    elem = b.find_element_by_xpath('//input[@value="Output"]')
    assert elem.get_attribute('checked') is None
    assert elem.get_attribute('disabled')

@util.requires_display
def test_mean_sst_monthly():
    b.get('http://localhost/portal/compmap.html')

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
def test_wave_watch():
    b.get('http://localhost/portal/compmap.html')

    util.clear_cache('WAV')

    b.select_param('variable', 'Mean Wave Direction')
    b.ensure_selected('plottype', 'Waverose')
    b.ensure_selected('period', 'Monthly')
    b.select_param('month', 'October') # September and October had a bug
    b.ensure_selected('dataset', 'WaveWatch III')

    elem = b.find_element_by_id('latitude')
    elem.send_keys("45")
    elem.send_keys(Keys.TAB)

    elem = b.switch_to_active_element()
    elem.send_keys("-145")

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
