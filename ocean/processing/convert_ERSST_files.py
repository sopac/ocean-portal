# Simple script to update ERSST file format to avoid NCO utility bug.
#
# This process converts the NetCDF SST data from Short (Scale Factor x Value plus Offset)
# format to Float.  This is necessary to avoid a bug in NCO utility that handles this data
# type incorrectly and results in incorrect processed values when calculating multi-month means.
import glob
import os
import subprocess
 
input_dir = '/data/sst/ersst/data/monthly/'
output_dir = '/data/sst/ersst/data/monthly_processed/'
input_files = glob.glob(input_dir + 'ersst.*.nc')
 
for input_file in input_files:
    filename = os.path.split(input_file)[1]
    output_filename = os.path.join(output_dir, filename)
    cmd = 'ncea ' + input_file + ' ' + output_filename
    proc = subprocess.call(cmd, shell=True)
