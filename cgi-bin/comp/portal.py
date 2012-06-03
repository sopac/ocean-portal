#!/usr/bin/python

import sys
import cgi
import cgitb

import ocean.reynolds.reynolds as reynolds
import ocean.ww3.ww3 as ww3
import ocean.sealevel.seaLevel as sealevel

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
        response = "{error: building}"
    elif datasetStr == "ww3":
        response = ww3.process(form)
    elif datasetStr == "bran":
        response = "{error: building}"
    elif datasetStr == "sealevel":
        response = sealevel.process(form)
    print response
else:
    print "{}"

