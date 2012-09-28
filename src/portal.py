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
import cgi
import json

import ocean.util as util

config = util.get_server_config()

if config['debug']:
    import cgitb
    cgitb.enable()

if 'PORTALPATH' in os.environ:
    os.environ['PATH'] = os.environ['PORTALPATH']

def main():
    form = cgi.FieldStorage()

    response = {}

    if 'dataset' in form:

        dataset = form['dataset'].value

        try:
            module = __import__('ocean.%s.%s' % (dataset, dataset), fromlist=[''])
            response.update(module.process(form))
        except ImportError:
            response['error'] = "Unknown dataset '%s'" % (dataset)
    else:
        response['error'] = "No dataset specified"

    print 'Content-Type: application/json'
    print 'X-Portal-Version: %s' % util.__version__
    print

    json.dump(response, sys.stdout)

if __name__ == '__main__':
    if config.get('profile', False):
        import cProfile
        cProfile.run('main()', '/tmp/portal.profile')
    else:
        main()
