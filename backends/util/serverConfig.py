"""
Store the server specific configurations

Author: Sheng Guo

(c) Climate and Oceans Support Program for the Pacific(COSPPAC)
    Bureau of Meteorology, Australia

Don't import config directly, use util.get_server_config()
"""

servers = {
    'tuscany': { 'hostname':  'tuscany.bom.gov.au',
                 # path on web server
                 'baseURL':   '/portal/',
                 # relative path to rasters
                 'rasterURL': 'raster/',
                 # path on disk to output rasters/caches
                 'outputDir': '/data/comp/raster/',
                 # relative path to caches (relative to rasterURL)
                 'cacheDir': { 'reynolds': 'cache/reynolds/',
                               'ersst': 'cache/ersst/'
                             },
                 # path to data on disk
                 'dataDir':  { 'reynolds': '/data/sst/reynolds/',
                               'ww3': '/data/wavewatch3/',
                               'sealevel': '/data/sea_level/',
                               'ersst': '/data/sst/ersst/data/',
                               'bran': '/data/blue_link/data/'
                             },
                 'mapservPath': '/usr/libexec/mapserv',
                 'debug':       True,
               },
    'tunceli': { 'hostname':  'tunceli.bom.gov.au',
                 'baseURL':   '/portal/',
                 'rasterURL': 'raster/',
                 'outputDir': '/data/comp/raster/',
                 'cacheDir': { 'reynolds': 'cache/reynolds/',
                               'ersst':    'cache/ersst/',
                             },
                 'dataDir':  { 'reynolds': '/data/comp/reynolds/',
                               'ww3':      '/data/comp/wavewatch3/',
                               'sealevel': '/data/comp/sea_level/',
                               'ersst':    '/data/comp/ersst/',
                               'bran':     '/data/comp/bran/',
                             },
                 'mapservPath': '/usr/libexec/mapserv',
                 'debug':       True,
               },
    'www4': { 'hostname':  'wdev.bom.gov.au',
              'baseURL':   '/cosppac/portal/',
              'rasterURL': 'raster/',
              'outputDir': '/web/cosppac/raster/',
              'cacheDir': { 'reynolds': 'cache/reynolds/',
                            'ersst':    'cache/ersst/',
                          },
              'dataDir':  { 'reynolds': '/web/data/cosppac/reynolds/',
                            'ww3':      '/web/data/cosppac/wavewatch3/',
                            'sealevel': '/web/data/cosppac/sea_level/',
                            'ersst':    '/web/data/cosppac/ersst/',
                            'bran':     '/web/data/cosppac/bran/',
                          },
              'mapservPath': '/usr/libexec/mapserv',
              'debug':       True,
            },
}
