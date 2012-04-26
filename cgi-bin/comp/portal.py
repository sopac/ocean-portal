#!/usr/bin/python

import sys
import reynolds
import cgi
import cgitb


sys.stderr = sys.stdout
cgitb.enable()

form = cgi.FieldStorage()

print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers

outputHTML = "" 

if "dataset" in form:

    datasetStr = form["dataset"].value
    if datasetStr == "reynolds":
        outputHTML = reynolds.process(form)
    elif datasetStr == "ersst":
        outputHTML = "{error: building}"


    print outputHTML
else:
    #Print the html
    print "{}"

