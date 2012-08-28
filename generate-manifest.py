#!/usr/bin/env python

import os, os.path
from setup import *

try:
    os.unlink('MANIFEST')
except OSError:
    pass

manifest = open('MANIFEST.in', 'w')
print >> manifest, "# generated by generate-manifest.py"
print >> manifest, 'include generate-manifest.py'

for d in data:
    print >> manifest, 'include %s' % d
for r in backend_resources:
    print >> manifest, 'include %s' % os.path.join('backends', 'resource', r)

manifest.close()
