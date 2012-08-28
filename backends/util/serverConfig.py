"""
Store the server specific configurations

Author: Sheng Guo

(c) Climate and Oceans Support Program for the Pacific(COSPPAC)
    Bureau of Meteorology, Australia

Don't import config directly, use util.get_server_config()
"""

servers = {
    'tuscany': { 'hostname':  'tuscany.bom.gov.au',
                 'baseURL':   '/portal',
                 'outputDir': '/data/comp/raster/',
                 'cacheDir': { 'reynolds': '/data/comp/raster/cache/reynolds/',
                               'ersst': '/data/comp/raster/cache/ersst/'
                             },
                 'dataDir':  { 'reynolds': '/data/sst/reynolds/',
                               'ww3': '/data/wavewatch3/',
                               'sealevel': '/data/sea_level/',
                               'ersst': '/data/sst/ersst/data/',
                               'bran': '/data/blue_link/data/'
                             },
                 'mapImageDir': '/data/maps/raster/',
                 'mapservPath': '/var/www/cgi-bin/mapserv',
                 'debug':       True,
               },
    'tunceli': { 'hostname':  'tunceli.bom.gov.au',
                 'baseURL':   '/portal',
                 'outputDir': '/data/comp/raster/',
                 'cacheDir': { 'reynolds': '/data/comp/raster/cache/reynolds/',
                               'ersst':    '/data/comp/raster/cache/ersst/',
                             },
                 'dataDir':  { 'reynolds': '/data/comp/reynolds/',
                               'ww3':      '/data/comp/wavewatch3/',
                               'sealevel': '/data/comp/sea_level/',
                               'ersst':    '/data/comp/ersst/',
                               'bran':     '/data/comp/bran/',
                             },
                 'mapImageDir': '/data/maps/raster/',
                 'mapservPath': '/usr/libexec/mapserv',
                 'debug':       True,
               },
    'www4': { 'hostname':  'www4.bom.gov.au:50002', # FIXME: will be proxied
              'baseURL':   '/cosppac/portal',
              'outputDir': '/data/comp/raster/',
              'cacheDir': { 'reynolds': '/data/comp/raster/cache/reynolds/',
                            'ersst':    '/data/comp/raster/cache/ersst/',
                          },
              'dataDir':  { 'reynolds': '/data/comp/reynolds/',
                            'ww3':      '/data/comp/wavewatch3/',
                            'sealevel': '/data/comp/sea_level/',
                            'ersst':    '/data/comp/ersst/',
                            'bran':     '/data/comp/bran/',
                          },
              'mapImageDir': '/data/maps/raster/',
              'mapservPath': '/usr/libexec/mapserv',
              'debug':       True,
               },
}
