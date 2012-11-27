#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import pytest
from _pytest.runner import call_and_report, BaseReport

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

# @pytest.mark.tryfirst
# def pytest_runtest_protocol(item, nextitem):
#     """
#     Handles marker-specific test requirements
#     """
# 
# 
#     # the unstable marker means we should try a test several times
#     if 'unstable' in item.keywords:
#         tries = item.keywords['unstable'].kwargs.get('tries', 3)
#         assert tries > 0
# 
#         item.ihook.pytest_runtest_logstart(nodeid=item.nodeid,
#                                            location=item.location)
# 
#         rep = call_and_report(item, 'setup')
# 
#         if rep.passed:
#             reports = []
#             for i in xrange(tries):
#                 reports.append(call_and_report(item, 'call', log=False))
#                 if rep.passed:
#                     break
# 
#             item.ihook.pytest_runtest_logreport(report=UnifiedReport(reports))
# 
#         call_and_report(item, 'teardown', nextitem=nextitem)
# 
#         return True
# 
# class UnifiedReport(BaseReport):
#     """
#     A collection of reports, as used by the 'unstable' marker
#     """
# 
#     def __init__(self, reports=[]):
#         self.reports = reports
# 
#     def toterminal(self, out):
#         for i, r in enumerate(self.reports):
#             out.sep('~', title="Attempt #%i" % (i + 1))
#             try:
#                 r.toterminal(out)
#             except Exception as e:
#                 pass
# 
#     @property
#     def passed(self):
#         return any([r.passed for r in self.reports])
# 
#     @property
#     def failed(self):
#         return all([r.failed for r in self.reports])
# 
#     @property
#     def skipped(self):
#         return all([r.skipped for r in self.reports])
# 
#     @property
#     def outcome(self):
#         if self.skipped:
#             return 'skipped'
#         elif self.failed:
#             return 'failed'
#         else:
#             return 'passed'
# 
#     def __getattr__(self, attr):
#         if attr in self.__dict__:
#             return BaseReport.__getattr__(self, attr)
# 
#         f = lambda r: getattr(r, attr)
#         v = f(self.reports[0])
# 
#         # sanity check
#         assert all([v == f(r) for r in self.reports[1:]])
# 
#         return v
