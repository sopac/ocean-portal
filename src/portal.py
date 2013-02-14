#!/usr/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import os
import sys
import json

import matplotlib
matplotlib.use('agg')

from ocean import util
from ocean.core import ReportableException
from ocean.config import get_server_config
from ocean.datasets import Dataset

config = get_server_config()

if config['debug']:
    import cgitb
    cgitb.enable()

if 'PORTALPATH' in os.environ:
    os.environ['PATH'] = os.environ['PORTALPATH']

def main():
    response = {}

    try:
        params = Dataset.parse(validate=False)
        ChosenDataset = util.import_dataset(params['dataset'])

        # reparse the params with the module, this time with validation
        params = ChosenDataset.parse()

        ds = ChosenDataset()

        response.update(ds.process(params))
    except ReportableException as e:
        response['error'] = e.message
    except ImportError:
        if config['debug']:
            raise
        else:
            response['error'] = "Unknown dataset '%s'" % (dataset)
    except Exception as e:
        if config['debug']:
            raise
        else:
            response['error'] = "Unable to handle your request (%s)" % e.message

    print 'Content-Type: application/json; charset=utf-8'
    print 'X-Portal-Version: %s' % util.__version__
    print

    json.dump(response, sys.stdout)

if __name__ == '__main__':
    if config.get('profile', False):
        import cProfile

        cProfile.run('main()', '/tmp/portal.profile.%s' % os.getpid())
    else:
        main()
