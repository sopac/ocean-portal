#!/usr/bin/env python

src = [
    'getMap',
    'portal.py',
]

backends = [
    'bran',
    'ersst',
    'netcdf',
    'reynolds',
    'sealevel',
    'util',
    'ww3',
]

# run generate-manifest.py after editing these sections
backend_resources = [
    'east.pgw',
    'subeast.pgw',
    'west.pgw',
    'subwest.pgw',
]

BASE_PATH = 'share/portal'
data = [
    'css/sst.css',
    'css/controlPanel.css',
    'css/comp/controlPanel.css',
    'config/regions.json',
    'config/datasets.json',
    'config/period.json',
    'config/comp/datasets.json',
    'config/comp/period.json',
    'config/comp/tidalGauges.txt',
    'config/comp/countryList.json',
    'html/controlPanel.html',
    'html/oceanmap.html',
    'html/sst.html',
    'html/compmap.html',
    'html/sstdev.html',
    'js/sstdev.js',
    'js/controlPanel.js',
    'js/comp/controlPanel.js',
    'js/comp/compmap.js',
    'js/map.js',
    'js/sst.js',
    'maps/reynolds.map',
]
if __name__ == '__main__':
    from distutils.core import setup
    import os.path
    import itertools

    setup(name='map-portal',
          version='0.1.0',
          author='COMP',
          author_email='COSPPac_COMP_Unit@bom.gov.au',
          url='http://tuscany/wiki/',
          packages=[ 'portal.backends' ] +
                   [ 'portal.backends.%s' % b for b in backends ],
          package_dir={
              'portal.backends': 'backends',
          },
          package_data={
              'portal.backends': [ os.path.join('resource', r)
                                    for r in backend_resources ],
          },
          scripts=[ os.path.join('src', s) for s in src ],
          data_files = [ (os.path.join(BASE_PATH, d), list(f))
            for d, f in itertools.groupby(data, lambda e: os.path.dirname(e)) ]
         )
