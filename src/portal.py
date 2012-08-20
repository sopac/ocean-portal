#!/usr/bin/python

import sys
import cgi

import ocean.reynolds.reynolds as reynolds
import ocean.ww3.ww3 as ww3
import ocean.sealevel.seaLevel as sealevel
import ocean.ersst.ersst as ersst
import ocean.bran.bran as bran
import ocean.utl.serverConfig as sc

if sc.servers[sc.currentServer]['debug']:
    import cgitb
    sys.stderr = sys.stdout
    cgitb.enable()

form = cgi.FieldStorage()

print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers


if "dataset" in form:
    """
    process request and respond the result in JSON format.
    """
    response = "{}"
    datasetStr = form["dataset"].value
    if datasetStr == "reynolds":
        response = reynolds.process(form)
    elif datasetStr == "ersst":
        response = ersst.process(form)
    elif datasetStr == "ww3":
        response = ww3.process(form)
    elif datasetStr == "bran":
        response = bran.process(form)
#        response = {"error": "building"} 
    elif datasetStr == "sealevel":
        response = sealevel.process(form)
    print response
else:
    print "{}"

