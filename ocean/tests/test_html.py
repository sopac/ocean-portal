#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import os.path
import subprocess

import ocean

def test_html_validates():
    # FIXME: find this file on the disk more reliably
    path = os.path.join(ocean.__path__[0], '..', 'html', 'compmap.html')
    subprocess.check_call(['xmllint', path])
