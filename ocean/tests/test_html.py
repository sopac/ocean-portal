#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import subprocess

def test_html_validates():
    # FIXME: find this file on the disk more reliably
    subprocess.check_call(['xmllint', 'html/compmap.html'])
