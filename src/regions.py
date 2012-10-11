#!/usr/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import os
import sys
import cgi
import json

import ocean.util as util
import ocean.util.regionConfig as rc

config = util.get_server_config()

if config['debug']:
    import cgitb
    cgitb.enable()

if 'PORTALPATH' in os.environ:
    os.environ['PATH'] = os.environ['PORTALPATH']

def __main__():
    form = cgi.FieldStorage()

    response = []

    try:
        portal = form['portal'].value
    except KeyError:
        portal = None

    etag = '"%s"' % util.__version__

    try:
        if os.environ['HTTP_IF_NONE_MATCH'] == etag:
            print 'Status: 304 Not Modified'
            print 'X-Portal-Version: %s' % util.__version__
            print
            return
    except KeyError:
        pass

    for abbr, (group, extents, name, opts) in rc.regions.items():
        # only take matching requests
        if portal and group and \
           portal != group:
            continue

        response.append({
            'name': name,
            'abbr': abbr,
            'extent': [extents['llcrnrlon'],  # left
                       extents['llcrnrlat'],  # bottom
                       extents['urcrnrlon'],  # right
                       extents['urcrnrlat']], # top
        })

    print 'Status: 200 Ok'
    print 'Content-Type: application/json; charset=utf-8'
    print 'ETag: %s' % etag
    print 'Cache-Control: max-age=3600' # FIXME: value?
    print 'X-Portal-Version: %s' % util.__version__
    print

    json.dump(response, sys.stdout)

if __name__ == '__main__':
    __main__()
