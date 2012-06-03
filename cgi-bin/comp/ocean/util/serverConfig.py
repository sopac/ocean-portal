"""
Store the server specific configurations

Author: Sheng Guo
(c)Climate and Oceans Support Program for the Pacific(COSPPAC), Bureau of Meteorology, Australia
"""
servers = {"tuscany": {"hostname": "tuscany.bom.gov.au",
                       "baseURL": "http://tuscany.bom.gov.au/dev",
                       "outputDir": "/data/comp/raster/",
                       "cacheDir": {"reynolds": "/data/comp/raster/cache/reynolds/"
                                   },
                       "dataDir": {"reynolds": "/data/sst/reynolds/",
                                   "ww3": "/data/wavewatch3/",
                                   "sealevel": "/data/sea_level/"
                                  },
                       "mapImageDir": "/var/www/cgi-bin/data/maps/raster/"
                      },
           "wdev": {
                   },
           "www": {
                  },
           "clim": {
                   }

}


currentServer = "tuscany"
