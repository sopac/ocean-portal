#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import os
import shutil
import json
import datetime

import pytest

from ocean.config import get_server_config

config = get_server_config()

def pytest_generate_tests(metafunc):
    if 'variable' in metafunc.fixturenames:
        # run the test for all possible variables
        variables = metafunc.module.Dataset.__variables__
        metafunc.parametrize('variable', variables)

    if 'period' in metafunc.fixturenames:
        # run the test for all possible periods
        periods = metafunc.module.Dataset.__periods__
        metafunc.parametrize('period', periods)

class JSONEncoder(json.JSONEncoder):
    """
    Extend JSONEncoder to serialize datetimes.
    """

    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)

class Report(object):
    """
    A class to generate a report.
    """

    def __init__(self):
        self._reports = []

        if 'WORKSPACE' in os.environ and \
           'BUILD_NUMBER' in os.environ:
            self._testdir = os.path.join(os.environ['WORKSPACE'],
                                         'test-reports',
                                         os.environ['BUILD_NUMBER'])
        else:
            # FIXME: make unique, write into the header
            self._testdir = '/tmp/test-report/'

        os.makedirs(self._testdir)

    def report(self, params, img):
        img = os.path.basename(img)
        file = os.path.join(config['outputDir'], img)

        assert os.path.exists(file)
        assert not os.path.exists(os.path.join(self._testdir, img))

        shutil.copy(file, self._testdir)

        self._reports.append({ 'params': params, 'img': img })

    def output(self):
        with open(os.path.join(self._testdir, 'report.json'), 'w') as f:
            json.dump(self._reports, f, cls=JSONEncoder, indent=2)

@pytest.fixture(scope='session')
def report(request):

    r = Report()

    request.addfinalizer(lambda *args: r.output())

    return r
