#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#         All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

"""
Tests should be defined as:
    def test_badger(b, url, ...):
        b.get(url)
        ...
"""

import os

import pytest

from uiutil import MapPortalDriver

def pytest_addoption(parser):
    # add a --url option which overrides the value of the 'url' parameter
    # passed to tests
    parser.addoption('--url', action='store',
                     default='http://localhost/portal/compmap.html')

@pytest.fixture(scope='session')
def b(request):
    if 'DISPLAY' not in os.environ:
        pytest.skip('Test requires display server (export DISPLAY)')

    b = MapPortalDriver()
    b.set_window_size(1200, 800)

    request.addfinalizer(lambda *args: b.quit())

    return b

@pytest.fixture
def url(request):
    return request.config.option.url
