#
# (c) 2013 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import csv
import os
import warnings

import pytest

from ocean import logger

@pytest.fixture
def log():
    try:
        os.unlink('/tmp/test-log.csv')
    except OSError:
        pass

    return logger._Logger('/tmp', 'test-log.csv')

@pytest.fixture
def warnings_as_errors(request):
    warnings.simplefilter('error')

    request.addfinalizer(lambda *args: warnings.resetwarnings())

def test_singleton():
    import ocean.logger

    assert logger == ocean.logger
    assert logger._logger == ocean.logger._logger

def test_logging(log):
    log.log('Item 1', 'Item 2')

    with open('/tmp/test-log.csv') as f:
        reader = csv.reader(f)

        lines = [ r for r in reader ]

        assert len(lines) == 2

        comment, row = lines

        assert comment[0][0] == '#'
        assert len(row) == 3
        assert row[1:] == ['Item 1', 'Item 2']

def test_timers(log):

    log.start_timer('method')
    elapsed = log.stop_timer('method')

    assert elapsed > 0
    assert isinstance(elapsed, float)

    with open('/tmp/test-log.csv') as f:
        reader = csv.reader(f)

        lines = [ r for r in reader ]

        assert len(lines) == 2

        comment, row = lines

def test_timers_warn(log, warnings_as_errors):

    log.start_timer('method')

    dt = log._timers['method']

    with pytest.raises(RuntimeWarning):
        log.start_timer('method')

    assert dt == log._timers['method']

def test_timers_fail(log):

    with pytest.raises(KeyError):
        log.stop_timer('method')

def test_timers_fail2(log):

    log.start_timer('method')
    log.stop_timer('method')

    with pytest.raises(KeyError):
        log.stop_timer('method')

def test_timers_reuse(log, warnings_as_errors):

    log.start_timer('method')

    dt = log._timers['method']

    log.stop_timer('method')
    log.start_timer('method')

    assert dt < log._timers['method']

def test_timers_decorator(log, warnings_as_errors):

    @log.time_and_log
    def time_me():
        return 'badger'

    a = time_me()
    assert a == 'badger'

    with open('/tmp/test-log.csv') as f:
        reader = csv.reader(f)

        lines = [ r for r in reader ]

        assert len(lines) == 2

        _, (_, name, _) = lines

        assert name == 'time_me'

def test_timers_decorator2(log, warnings_as_errors):

    @log.time_and_log('some-other-name')
    def time_me():
        return 'badger'

    a = time_me()
    assert a == 'badger'

    with open('/tmp/test-log.csv') as f:
        reader = csv.reader(f)

        lines = [ r for r in reader ]

        assert len(lines) == 2

        _, (_, name, _) = lines

        assert name == 'some-other-name'
