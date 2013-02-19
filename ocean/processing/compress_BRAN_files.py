#!/usr/bin/env python
"""
Title: compress_BRAN_files.py
Author: Nicholas Summons, n.summons@bom.gov.au
CreationDate: 2012-07-23

Description: 
            Utility for compressing BRAN (Bluelink ReANalysis) NetCDF files 
            to a third of the size.  This is acheived by converting the files to 
            NetCDF-4 format with compression turned on and removing depth
            levels below 300m.
            
            To use, pass a filename or multiple files (using the wild card) as
            an input argument.
            
            Examples:
                    
                    python compress_BRAN_files.py ocean_temp_1991_01_01.nc
                    
                    python compress_BRAN_files.py ocean_temp*.nc
"""
import os
import sys
import numpy
import netCDF4 as nc
import datetime
import pdb
from glob import glob 


if len(sys.argv) > 2:
    # Handles case where unix shell has pre-expanded wildcards
    filelist = sys.argv[1:]
elif len(sys.argv) == 2:
    # Expand wildcards
    filelist = glob(sys.argv[1])
else:
    # Display help if no arguments provided
    print __doc__
    filelist = []

# Loop through selected files
for inputFilename in filelist:

    filePath, fileName = os.path.split(inputFilename)
    fileHead, fileExt = os.path.splitext(fileName)

    # Skip if file is an old output file
    if fileExt == '.nc4':
        continue

    print 'Processing ' + inputFilename
    
    # Create output file
    outputFilename = fileHead + '.nc4'
    referenceNc = nc.Dataset(inputFilename)
    outputNc = nc.Dataset(outputFilename, 'w', format='NETCDF4')

    # Determine depth levels for top 300m
    if referenceNc.variables.has_key('zt_ocean'):
        depthLevels = referenceNc.variables['zt_ocean'][:]
        dimTop300m = len(numpy.flatnonzero(depthLevels < 300)) + 1
        depthLevels = depthLevels[0:dimTop300m]

    # Create dimensions
    for dimName1,dim1 in referenceNc.dimensions.iteritems():
        if dimName1 == 'zt_ocean':
            dimLen2 = dimTop300m
        else:
            dimLen2 = len(dim1)
        if dim1.isunlimited():
            dimLen2 = 0
        outputNc.createDimension(dimName1, dimLen2)

    # Copy variables
    for varName1,var1 in referenceNc.variables.iteritems():

        if var1.ndim == 1:
            var2 = outputNc.createVariable(varName1, var1.dtype, var1.dimensions)
            for attr in var1.ncattrs():
                if attr == '_FillValue':
                    continue
                var2.setncattr(attr, var1.getncattr(attr))
            if varName1 == 'zt_ocean':
                var2[:] = depthLevels
            else:
                var2[:] = var1[:]
        else:
            dataVar = outputNc.createVariable(varName1, var1.dtype, var1.dimensions, zlib=True, complevel=6, 
                                              fill_value = -999)
            for attr in var1.ncattrs():
                if attr == '_FillValue':
                    continue
                dataVar.setncattr(attr, var1.getncattr(attr))
            dims = dataVar.shape
            if len(dims) == 2:
                dataVar[:,:] = var1[:dims[0],:dims[1]]
            elif len(dims) == 3:
                dataVar[:,:,:] = var1[:dims[0],:dims[1],:dims[2]]
            elif len(dims) == 4:
                dataVar[:,:,:,:] = var1[:dims[0],:dims[1],:dims[2],:dims[3]]

    # Copy global attributes
    attdict = referenceNc.__dict__
    attdict['filename'] = unicode(outputFilename)
    attdict['history'] = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%MZ") + \
                         ': Converted to NetCDF4 with compression and 300m depth subsetting to reduce file size.  ' + \
                         attdict['history']
    for attr in attdict:
        outputNc.setncattr(attr, attdict[attr])

    # Save data and close files
    outputNc.sync()
    outputNc.close()
    referenceNc.close()
