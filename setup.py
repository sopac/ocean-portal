#!/usr/bin/env python

NAME                = 'map-portal'
VERSION             = '0.1.0'
DESCRIPTION         = 'Map Portal'
LONG_DESCRIPTION    = """\
COMP Group Climate Portal
"""
AUTHOR              = 'COMP'
AUTHOR_EMAIL        = 'COSPPac_COMP_Unit@bom.gov.au'
URL                 = 'http://tuscany.bom.gov.au/wiki/index.php/Map_Portal'

rpm_deps = [
    'basemap >= 1.1.7',
    'mapserver-python >= 6.0.1',
    'matplotlib >= 1.1.0',
    'netCDF4 >= 0.9.7',
    'numpy >= 1.6.1',
    'scipy >= 0.9.0',
]

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
html = [
    'sst.html',
    'compmap.html',
]

data = [
    'css/common.css',
    'css/sst.css',
    'css/comp/controlPanel.css',
    'config/comp/datasets.json',
    'config/comp/period.json',
    'config/comp/tidalGauges.txt',
    'config/comp/countryList.json',
    'js/comp/controlPanel.js',
    'js/comp/compmap.js',
    'js/config.js',
    'js/sst.js',
    'maps/reynolds.map',
    'images/dot.png',
    'images/sst.png',
    'images/search.gif',
    'images/calendar-blue.gif',
    'images/blank.png',
    'images/download.png',
    'images/loading.gif',
    'images/notavail.png',
    'images/climate.jpg',
    'images/bom_logo.gif',
    'images/bathymetry_ver.png',
]

if __name__ == '__main__':
    from distutils.core import setup
    from distutils.command.bdist_rpm import bdist_rpm
    import os.path
    import itertools

    # add Requires: for RPM
    _original_make_spec_file = bdist_rpm._make_spec_file
    def _make_spec_file(*args):
        spec = _original_make_spec_file(*args)
        spec.insert(spec.index('%description') - 1,
                    'Requires: %s' % ', '.join(rpm_deps))
        return spec
    bdist_rpm._make_spec_file = _make_spec_file

    data_files = \
        [ ('/var/www/cgi-bin/portal', [ os.path.join('src', s) for s in src ]) ] + \
        [ (BASE_PATH, [ os.path.join('html', h) for h in html ]) ] + \
        [ (os.path.join(BASE_PATH, d), list(f))
            for d, f in itertools.groupby(data, lambda e: os.path.dirname(e)) ]

    setup(name=NAME,
          version=VERSION,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          url=URL,
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,

          packages=[ 'ocean' ] +
                   [ 'ocean.%s' % b for b in backends ],
          package_dir={
              'ocean': 'backends',
          },
          package_data={
              'ocean': [ os.path.join('resource', r)
                         for r in backend_resources ],
          },
          data_files = data_files,
         )
