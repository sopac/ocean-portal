#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import os.path

from distutils.core import Command
from distutils.util import convert_path

from distutils import log

from jsmin import JavascriptMinify

class build_web(Command):

    description = "Build (minify) web resources"

    user_options = [
        ('build-dir=', 'd', "directory to \"build\" to"),
        ('force', 'f', "forcibly build everything (ignore file timestamps"),
        ('compress', None, "Compress (minify) web resources"),
        ]

    boolean_options = [ 'force', 'compress' ]

    def initialize_options(self):
        self.build_dir = None
        self.build_base = None
        self.force = None
        self.compress = None
        self.web_files = []

        self.outfiles = []

    def finalize_options(self):
        self.set_undefined_options('build',
            ('build_base', 'build_base'),
            ('force', 'force'))

        if self.build_dir is None:
            self.build_dir = os.path.join(self.build_base, 'web')

        self.web_files = self.distribution.web_files[1]

    def get_source_files(self):
        return self.web_files

    def run(self):
        self.mkpath(self.build_dir)

        outfiles = []
        updated_files = []

        # consider replacing this with a better utility
        jsm = JavascriptMinify()

        for f in self.web_files:
            inf = convert_path(f)
            outf = os.path.join(self.build_dir, f)

            self.mkpath(os.path.dirname(outf))

            if self.compress:
                log.info("minifying %s -> %s" % (f, outf))

                input = open(inf, 'r')
                output = open(outf, 'wb')

                # copy 5 lines of the header
                for l in range(6):
                    output.write(input.readline())

                jsm.minify(input, output)
                input.close()
                output.close()
            else:
                self.copy_file(inf, outf)

            self.outfiles.append(outf)
