#
# (c) 2013 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import csv
import os
import os.path
import sys
from datetime import datetime
from warnings import warn

from ocean import config

cfg = config.get_server_config()

class _Logger(object):

    def __init__(self, path=None, filename=None):
        self._timers = {}

        if path is None:
            path = os.path.join(cfg['outputDir'], 'logs')

        if filename is None:
            filename = '%s.csv' % os.getpid()

        try:
            os.makedirs(path)
        except OSError:
            pass

        self.logfile = open(os.path.join(path, filename), 'a')
        self.writer = csv.writer(self.logfile, delimiter=' ')

        print >> self.logfile, "# %s instance started %s" % (
            sys.argv[0], datetime.now().strftime('%c'))

    def __del__(self):
        self.logfile.close()

    def log(self, *args):
        time = datetime.now()
        self.writer.writerow([time.isoformat()] + list(args))
        self.logfile.flush()

    def start_timer(self, timer_name):
        if timer_name in self._timers:
            warn("Timer %s already started" % timer_name, RuntimeWarning)
            return

        self._timers[timer_name] = datetime.now()

    def stop_timer(self, timer_name, log=True):
        time = datetime.now()
        delta = time - self._timers[timer_name]
        elapsed = delta.seconds + delta.microseconds / 1e6

        del self._timers[timer_name]

        if log:
            self.log(timer_name, elapsed)

        return elapsed

# singleton logger
_logger = _Logger()

# global methods
log = _logger.log
start_timer = _logger.start_timer
stop_timer = _logger.stop_timer
