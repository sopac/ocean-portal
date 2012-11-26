#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import pytest
from _pytest.runner import call_and_report

def pytest_generate_tests(__multicall__, metafunc):
    """
    Supports parametrised tests using generate_*() fns.

    Taken from GFE test suite.
    """

    __multicall__.execute()

    name = metafunc.function.__name__.replace('test_', 'generate_')
    fn = getattr(metafunc.module, name, None)
    if fn:
        fn(metafunc)

@pytest.mark.tryfirst
def pytest_runtest_protocol(item, nextitem):
    """
    Handles marker-specific test requirements
    """


    # the unstable marker means we should try a test several times
    if 'unstable' in item.keywords:
        retries = item.keywords['unstable'].kwargs.get('retries', 3)

        item.ihook.pytest_runtest_logstart(nodeid=item.nodeid,
                                           location=item.location)

        rep = call_and_report(item, 'setup')

        if rep.passed:
            for i in xrange(retries):
                rep = call_and_report(item, 'call')
                if rep.passed:
                    break

        call_and_report(item, 'teardown', nextitem=nextitem)

        return True
