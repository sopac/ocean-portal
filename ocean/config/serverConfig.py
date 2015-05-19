#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Author: Sheng Guo <s.guo@bom.gov.au>
#         Danielle Madeley <d.madeley@bom.gov.au>

"""
Store the server specific configurations

Don't import config directly, use ocean.config.get_server_config()
"""

from ocean.config import BaseConfig

class default(BaseConfig):
    """
    Default server config. Inherit this class to set per-server config.
    """

    # path on web server
    baseURL = '/portal/'

    # relative path to rasters
    rasterURL = 'raster/'

    # path on disk to output rasters/caches
    outputDir = '/data/comp/raster/'

    # relative path to caches (relative to rasterURL) (obsolete?)
    cacheDir = {
        'reynolds': 'cache/reynolds/',
        'ersst': 'cache/ersst/',
    }

    dataDir = {}

    mapservPath = '/usr/libexec/mapserv'
    debug = False
    profile = False

class tuscany(default):
    debug = True
    mapservPath = '/usr/libexec/mapserver'
    dataDir = {
        'bran': '/data/blue_link/data/',
        'ersst': '/data/sst/ersst/data/',
        'reynolds': '/data/sst/reynolds/',
        'sealevel': '/data/sea_level/',
        'ww3': '/data/wavewatch3/',
        'coral':'/data/sst/coral/',
        'poamasla':'/data/poama/',
        'poamassta':'/data/poama/',
        'oceanmaps':'/data/oceanmaps/',
        'chloro':'/data/chloro/',
        'currents':'/data/currents/',
        'ww3forecast':'/data/wavewatch3/forecast/'
    }

class tunceli(default):
    debug = True

    # shared data directories from ITB (mounted rw)
    dataDir = {
        'bran': '/www4/data/cosppac/bran/',
        'ersst': '/www4/data/cosppac/ersst/',
        'reynolds': '/www4/data/cosppac/reynolds/',
        'sealevel': '/www4/data/cosppac/sea_level/',
        'ww3': '/www4/data/cosppac/wavewatch3/',
        'coral':'/www4/data/cosppac/coral/',
        'coral_ol':'/www4/data/cosppac/coral/',
        'poamasla':'/www4/data/cosppac/poama/',
        'poamassta':'/www4/data/cosppac/poama/',
        'oceanmaps':'/www4/data/cosppac/oceanmaps/',
        'chloro':'/www4/data/cosppac/chloro/',
        'currents':'/www4/data/cosppac/currents/',
        'ww3forecast':'/www4/data/cosppac/wavewatch3/forecast/'
    }

class www4(default):
    debug = True
    baseURL = '/cosppac/apps/portal/'
    outputDir = '/web/cosppac/raster/'

    dataDir = {
        'bran': '/web/data/cosppac/bran/',
        'ersst': '/web/data/cosppac/ersst/',
        'reynolds': '/web/data/cosppac/reynolds/',
        'sealevel': '/web/data/cosppac/sea_level/',
        'ww3': '/web/data/cosppac/wavewatch3/',
        'coral': '/web/data/cosppac/coral/',
        'coral_ol': '/web/data/cosppac/coral/',
        'poamasla':'/web/data/cosppac/poama/',
        'poamassta':'/web/data/cosppac/poama/',
        'oceanmaps': '/web/data/cosppac/oceanmaps/',
        'chloro':'/web/data/cosppac/chloro/',
        'currents':'/web/data/cosppac/currents/',
        'ww3forecast':'/web/data/cosppac/wavewatch3/forecast/'
    }

class hoapp2(www4):
    debug = False
