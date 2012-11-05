# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#         All Rights Reserved
#
#     Authors: Danielle Madeley <d.madeley@bom.gov.au>

import pytest

def pytest_addoption(parser):
    parser.addoption('--url', action='store',
                     default='http://localhost/portal/compmap.html')

@pytest.fixture
def url(request):
    return request.config.option.url
