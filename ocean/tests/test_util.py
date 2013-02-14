#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import datetime

import pytest

import ocean
from ocean import util

def test_get_resource():
    p = util.get_resource('maps', 'raster.map')
    assert p.startswith(ocean.__path__[0])
    assert p.endswith('maps/raster.map')

def test_build_response_object():
    o = util.build_response_object(
        ['a', 'b', 'c'],
        'canoe',
        ['.png', '.jpg', '.txt'])

    assert o == {
        'a': 'canoe.png',
        'b': 'canoe.jpg',
        'c': 'canoe.txt',
    }

def test_format_old_date():
    d = datetime.date(1900, 1, 1)
    ds = util.format_old_date(d)

    assert ds == 'January 1900'

    d = datetime.date(2000, 3, 1)
    ds = util.format_old_date(d)

    assert ds == 'March 2000'

    d = datetime.date(1850, 5, 1)
    ds = util.format_old_date(d)

    assert ds == 'May 1850'

def test_funcregister_good():
    class Test(object):
        apply_to = util.Parameterise()

        @apply_to(variable='mean')
        def get_filename(self, params={}):
            return 'canoe'

        @apply_to(variable='anom')
        def get_filename(self, params={}):
            return 'yacht'

    t = Test()

    assert t.get_filename(params={ 'variable': 'mean'}) == 'canoe'
    assert t.get_filename(params={ 'variable': 'anom'}) == 'yacht'

    with pytest.raises(AttributeError) as e:
        t.get_filename(params={ 'variable': 'dec' })

    assert e.value.message.startswith('No function')

def test_funcregister_ambiguous():
    class Test(object):
        apply_to = util.Parameterise()

        @apply_to(variable='mean')
        def get_filename(self, params={}):
            return 'canoe'

        @apply_to(period='monthly')
        def get_filename(self, params={}):
            return 'yacht'

    t = Test()

    with pytest.raises(AttributeError) as e:
        t.get_filename(params={ 'variable': 'mean', 'period': 'monthly' })

    assert e.value.message.startswith('Ambiguous')

def test_funcregister_good_multi():
    class Test(object):
        apply_to = util.Parameterise()

        @apply_to(variable='mean', period='monthly')
        def get_filename(self, params={}):
            return 'Monthly Mean'

        @apply_to(variable='anom', period='monthly')
        def get_filename(self, params={}):
            return 'Monthly Anom'

    t = Test()
    t.badger = 1

    assert t.get_filename(params={ 'variable': 'mean', 'period': 'monthly' }) \
        == 'Monthly Mean'
    assert t.get_filename(params={ 'variable': 'anom', 'period': 'monthly' }) \
        == 'Monthly Anom'

    with pytest.raises(AttributeError) as e:
        t.get_filename(params={ 'variable': 'dec', 'period': 'monthly' })

    assert e.value.message.startswith('No function')

def test_funcregister_tight_binding_good():
    class Test(object):
        apply_to = util.Parameterise()

        @apply_to()
        def get_title(self, params={}):
            return 'Monthly Average'

        @apply_to(variable='anom')
        def get_title(self, params={}):
            return 'Monthly Anom'

    t = Test()

    assert t.get_title(params=dict(variable='mean')) == 'Monthly Average'
    assert t.get_title(params=dict(variable='anom')) == 'Monthly Anom'
    assert t.get_title(params={}) == 'Monthly Average'

def test_funcregister_tight_binding_ambiguous():
    class Test(object):
        apply_to = util.Parameterise()

        @apply_to(period='monthly')
        def get_title(self, params={}):
            return 'Monthly Average'

        @apply_to(variable='anom')
        def get_title(self, params={}):
            return 'Monthly Anom'

    t = Test()

    with pytest.raises(AttributeError) as e:
        t.get_title(params=dict(variable='anom', period='monthly'))

    assert e.value.message.startswith('Ambiguous')

def test_funcregister_ignore():
    class Test(object):
        apply_to = util.Parameterise()

        @apply_to()
        def get_path(self, params={}):
            return '/usual/path'

        @apply_to(variable='dec')
        def get_path(self, params={}):
            return '/deciles/path'

    class TestSubClass(Test):
        apply_to = util.Parameterise(Test)

        @apply_to(period='monthly')
        def get_path(self, params={}):
            return '/original/data/path'

        @apply_to(period='monthly', variable='dec')
        def get_path(self, params={}):
            return self.get_path(params=params, _ignore=['period'])

    t = TestSubClass()

    assert t.get_path(params=dict(variable='anom',
                                  period='monthly')) == '/original/data/path'
    assert t.get_path(params=dict(variable='anom',
                                  period='3monthly')) == '/usual/path'
    assert t.get_path(params=dict(variable='dec',
                                  period='monthly')) == '/deciles/path'
    assert t.get_path(params=dict(variable='dec',
                                  period='3monthly')) == '/deciles/path'

def test_funcregister_subclass():
    class BaseTest(object):
        apply_to = util.Parameterise()

        @apply_to()
        def get_a(self, params={}):
            return 'a'

    class Lowercase(BaseTest):
        apply_to = util.Parameterise(BaseTest)

        @apply_to()
        def get_b(self, params={}):
            return 'b'

    class Uppercase(BaseTest):
        apply_to = util.Parameterise(BaseTest)

        @apply_to()
        def get_b(self, params={}):
            return 'B'

    t = Lowercase()
    T = Uppercase()

    assert t.get_a(params={}) == 'a'
    assert t.get_b(params={}) == 'b'
    assert T.get_a(params={}) == 'a' # yes, lowercase
    assert T.get_b(params={}) == 'B'
