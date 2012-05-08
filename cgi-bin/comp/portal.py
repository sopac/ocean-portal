#!/usr/bin/python

import sys
import cgi
import cgitb

import ocean.reynolds.reynolds as reynolds

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
    elif datasetStr == "wwiii":
        response = "{error: building}"
    elif datasetStr == "bran":
        response = "{error: building}"
    elif datasetStr == "sealevel":
        response = "{error: building}"
    print response
else:
    print "{}"

