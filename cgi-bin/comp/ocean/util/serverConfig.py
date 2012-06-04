"""
Store the server specific configurations

Author: Sheng Guo
(c)Climate and Oceans Support Program for the Pacific(COSPPAC), Bureau of Meteorology, Australia
"""
servers = {"tuscany": {"hostname": "tuscany.bom.gov.au",
                       "baseURL": "http://tuscany.bom.gov.au/dev",
                       "outputDir": "/home/mhowie/portal/images/",
                       "cacheDir": "/data/comp/raster/cache/ersst/",
                       "dataDir": "/data/sst/ersst/data/"
                      },
           "wdev": {
                   },
           "www": {
                  },
           "clim": {
                   }

}


currentServer = "tuscany"

