#!/usr/bin/env python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

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

scripts = [
    'replicate-portal-data',
    'cleanup-raster-cache',
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
    'maps/bathymetry.map',
    'maps/raster.map',
    'fonts/fonts.list',
    'fonts/Vera.ttf',
    'fonts/VeraMono.ttf',
]

map_layer_extensions = ['dbf', 'prj', 'shp', 'shx' ]
map_layers = [
    'bathymetry_0',
    'bathymetry_200',
    'bathymetry_1000',
    'bathymetry_2000',
    'bathymetry_3000',
    'bathymetry_4000',
    'bathymetry_5000',
    'bathymetry_6000',
    'bathymetry_7000',
    'bathymetry_8000',
    'bathymetry_9000',
    'bathymetry_10000',
    'ocean',
    'land',
    'coastline',
    'pacific_islands_capitals',
    'southern_pac',
    'World_Maritime_Boundaries',
]

BASE_PATH = 'share/portal'
html = [
#   'sst.html',
    'compmap.html',
]

script_substitutions = {
    # development version, compressed version
    'jquery.js': ('jquery-1.8.1.js', 'jquery-1.8.1.min.js'),
    'ext-all.js': ('ext-all-dev.js', 'ext-all.js'),
}

web_files = [
    'css/common.css',
#   'css/sst.css',
    'css/comp/controlPanel.css',
    'js/comp/controlPanel.js',
    'js/comp/compmap.js',
#   'js/sst.js',
]

data = [
    'config/comp/datasets.json',
    'config/comp/period.json',
    'config/comp/portals.json',
    'config/comp/tidalGauges.txt',
    'config/aus/countryList.json',
    'config/pac/countryList.json',
    'images/search.gif',
    'images/calendar-blue.gif',
    'images/blank.png',
    'images/loading.gif',
    'images/notavail.png',
    'images/climate.jpg',
    'images/bom_logo.gif',
    'images/bathymetry_ver.png',
]

# CODE BEGINS
import os.path

backend_resources += [ os.path.join('maps', 'layers', '%s.%s' % (l, ext))
                        for l in map_layers
                        for ext in map_layer_extensions ]

if __name__ == '__main__':
    from distutils.core import setup
    from distutils.command.bdist_rpm import bdist_rpm

    from localdistutils.dist import PortalDist
    from localdistutils.build import build
    from localdistutils.build_web import build_web
    from localdistutils.install import install
    from localdistutils.install_web import install_web

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
          scripts=[ os.path.join('src', s) for s in scripts ],
          data_files = data_files,

          # FIXME: BASE_PATH here is ignored because I'm lazy, BASE_PATH from
          # web_files is used
          html_files = (BASE_PATH,
                        [ os.path.join('html', h) for h in html ],
                        script_substitutions),
          web_files = (BASE_PATH, web_files),

          # extend distutils
          distclass=PortalDist,
          cmdclass={
              'build': build,
              'build_web': build_web,
              'install': install,
              'install_web': install_web,
          },
         )
