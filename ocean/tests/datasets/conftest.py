#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

def pytest_generate_tests(metafunc):
    if 'variable' in metafunc.fixturenames:
        # run the test for all possible variables
        variables = metafunc.module.Dataset.__variables__
        metafunc.parametrize('variable', variables)

    if 'period' in metafunc.fixturenames:
        # run the test for all possible periods
        periods = metafunc.module.Dataset.__periods__
        metafunc.parametrize('period', periods)
