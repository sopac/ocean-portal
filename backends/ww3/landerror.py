#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Jason Smith <jason.smith@bom.gov.au>

class LandError(Exception):
    
    def __init__(self,value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)
