#!/usr/bin/python

import sys
import cgi
import json

import ocean.util as util

config = util.get_server_config()

if config['debug']:
    import cgitb
    sys.stderr = sys.stdout
    cgitb.enable()

form = cgi.FieldStorage()

print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers

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

json.dump(response, sys.stdout)
