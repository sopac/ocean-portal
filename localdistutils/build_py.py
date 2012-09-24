#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

from distutils.command.build_py import build_py as real_build_py

import util

ver = util.get_version()

class build_py(real_build_py):

    def build_module(self, module, module_file, package):
        real_build_py.build_module(self, module, module_file, package)

        # append version to every module
        package = package.split('.')
        outfile = self.get_module_outfile(self.build_lib, package, module)

        with open(outfile, 'a') as module:
            print >> module
            print >> module, "__version__ = '%s'" % (ver)
