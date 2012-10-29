#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import os
from glob import glob

from ocean.config import get_server_config

config = get_server_config()

def clear_cache(product, filetype='*'):
    cachedir = config['outputDir']
    s = os.path.join(cachedir, '%s*.%s' % (product, filetype))

    for d in glob(s):
        try:
            os.unlink(d)
        except IOError:
            raise