#!/usr/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import sys
import cgi
import json

import ocean.util as util

config = util.get_server_config()

if config['debug']:
    import cgitb
    cgitb.enable()

form = cgi.FieldStorage()

print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers

response = {
    'version': util.__version__,
}

if 'dataset' in form:

    dataset = form['dataset'].value

    try:
        module = __import__('ocean.%s.%s' % (dataset, dataset), fromlist=[''])
        response.update(module.process(form))
    except ImportError:
        response['error'] = "Unknown dataset '%s'" % (dataset)
else:
    response['error'] = "No dataset specified"

json.dump(response, sys.stdout)
