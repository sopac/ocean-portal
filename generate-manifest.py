#!/usr/bin/env python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import os, os.path
from setup import *

try:
    os.unlink('MANIFEST')
except OSError:
    pass

manifest = open('MANIFEST.in', 'w')
print >> manifest, "# generated by generate-manifest.py"
print >> manifest, '''
include generate-manifest.py
include NEWS
recursive-include localdistutils *.py
'''

for d in data:
    print >> manifest, 'include %s' % d
for w in web_files:
    print >> manifest, 'include %s' % w
for r in backend_resources:
    print >> manifest, 'include %s' % os.path.join('ocean', 'resource', r)
for h in html:
    print >> manifest, 'include %s' % os.path.join('html', h)

manifest.close()
