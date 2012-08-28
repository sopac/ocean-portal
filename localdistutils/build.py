#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

from distutils.command.build import build as real_build

class build(real_build):

    sub_commands = real_build.sub_commands + [
        ('build_web', lambda *args: True),
    ]
