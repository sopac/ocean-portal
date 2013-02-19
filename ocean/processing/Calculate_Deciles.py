#!/usr/bin/env python
"""
Title: Calculate_Deciles.py
Author: Nicholas Summons, n.summons@bom.gov.au
CreationDate: 2012-11-13

Description: 
    Calculate deciles for a 2D variable stored in NetCDF files.
    Flag values of 0 and 11 signify lowest and highest on record respectively.

    Note: This script assumes each time slice is stored as a separate NetCDF file.
          The variable for calculating deciles is also assumed to have two 
          non-single length dimensions of 'lat', 'lon' for latitude and longitude
          values and to be in that order.

          E.g. the following format is acceptable:
               sst[time, zlevel, lat, lon] if time and zlevel are both single length dimensions.
"""
import numpy as np
import pdb
import netCDF4
import bisect
import glob
import os
import copy

class Calculate_Deciles(object):

    def __init__(self):
        pass

    def process(self, input_files, output_dir, variable_name):
     
        # Calculate decile edge values that define the range for each decile
        decile_edge_values = self.calculate_decile_edges(input_files, variable_name)
        
        # Open reference file for copying lat/lon values
        referenceNc = netCDF4.Dataset(input_files[0])
        
        for input_file in input_files:
            
            # Open input file and load data
            nc2 = netCDF4.Dataset(input_file, 'r')
            var = nc2.variables[variable_name][:]
            
            # Convert to 2D array by removing any single-length dimensions
            var = np.squeeze(var)
            dim1, dim2 = var.shape

            # Create array for recording deciles
            deciles = np.ma.empty_like(var)
            
            # Calculate deciles
            for k1 in range(dim1):
                for k2 in range(dim2):
                    if decile_edge_values.mask[:, k1, k2].any() or var.mask[k1, k2]:
                        deciles[k1, k2].mask = True
                    elif var[k1, k2] >= decile_edge_values[-1, k1, k2]:
                        # Handle highest on record case
                        deciles[k1, k2] = 11
                    else:
                        deciles[k1,k2] = np.searchsorted(decile_edge_values[:, k1, k2], var[k1,k2])

            # Open output file
            output_filename = os.path.splitext(input_file)[0] + '_dec.nc'
            output_filename2 = os.path.join(output_dir, os.path.split(output_filename)[1])
            outputNc = netCDF4.Dataset(output_filename2, 'w', format='NETCDF4')
            
            # Create dimensions
            for dimName, dim in referenceNc.dimensions.iteritems():
                if dimName in ['lat', 'lon']:
                    dimLen = len(dim)
                    if dim.isunlimited():
                        dimLen = 0
                    outputNc.createDimension(dimName, dimLen)

            # Create variables
            for varName1, var1 in referenceNc.variables.iteritems():
                if varName1 in ['lat', 'lon']:
                    var2 = outputNc.createVariable(varName1, var1.dtype, var1.dimensions)
                    for attr in var1.ncattrs():
                        if attr == '_FillValue':
                            continue
                        var2.setncattr(attr, var1.getncattr(attr))
                    var2[:] = var1[:]
                elif varName1 == variable_name:
                    dataVar = outputNc.createVariable(varName1 + '_deciles', var1.dtype, 
                                                      (u'lat', u'lon'), zlib=True, complevel=6)
                    dataVar.setncattr('long_name', 'Deciles 1-10 and flag values 0/11 for lowest/highest on record.')
                    dataVar.setncattr('units', 'Deciles')
                    dataVar[:,:,] = deciles[:,:]
                    #if len(np.where(np.isnan(deciles.data))[0]) > 0:
                    #    print 'Error!!!!!!!!!!!!!!'
                    #    print input_file
                    cat = copy.copy(deciles)
                    cat = np.where((cat >= 2) & (cat <= 3), 2, cat)
                    cat = np.where((cat >= 4) & (cat <= 7), 3, cat)
                    cat = np.where((cat >= 8) & (cat <= 9), 4, cat)
                    cat = np.where((cat == 10), 5, cat)
                    cat = np.where((cat == 11), 6, cat)
                    cat = cat + 1
                    dataVar2 = outputNc.createVariable(varName1 + '_dec_cats', var1.dtype,
                                                      (u'lat', u'lon'), zlib=True, complevel=6)
                    dataVar2.setncattr('long_name', 'Decile categories [1-7]')
                    dataVar2.setncattr('categories', 'Lowest on record, Very much below average [1], Below average [2-3], Average [4-7], Above average [8-9], Very much above average [10], Highest on record')
                    dataVar2.setncattr('units', '')
                    dataVar2[:,:,] = cat[:,:]

            # Save data and close files
            outputNc.sync()
            outputNc.close()
            nc2.close()

        referenceNc.close()        

    def calculate_decile_edges(self, input_files, variable_name):
        for file, k in zip(input_files, range(len(input_files))):
            # Open file and load data
            nc = netCDF4.Dataset(file, 'r')
            var = nc.variables[variable_name][:]
            
            # Convert to 2D array by removing any single-length dimensions
            var = np.squeeze(var) 
            
            # Construct 3D array to store 2D arrays for all time slices
            if k == 0:
                dim1, dim2 = var.shape
                var3D = np.ma.zeros([len(input_files), dim1, dim2])
            var3D[k,:,:] = var[:,:]
            nc.close()
           
        # Calculate decile edges
        percentiles = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        decile_edges = np.percentile(var3D, percentiles, axis=0)

        # Convert to masked arrays
        missing_values_mask = var3D.mask.any(axis=0)
        decile_edges = [np.ma.array(k, mask=missing_values_mask) for k in decile_edges]

        # Convert list of 2D arrays to 3D array
        decile_edges = np.ma.vstack(decile_edges).reshape(len(percentiles), dim1, dim2)
        return decile_edges


if __name__ == '__main__':

    product_list = ['reynolds', 'ersst']
    product = product_list[0]
    variable_name = 'sst'

    import Calculate_Deciles
    calc_dec = Calculate_Deciles.Calculate_Deciles()
    for avg_period in [1, 3, 6, 12]:
        for month in range(1, 12 + 1):
            month_str = '%02d' % month
            avg_period_str = '%d' % avg_period

            if avg_period == 1:
                if product == 'reynolds':
                    input_files = glob.glob('/data/sst/reynolds/averages/monthly/reynolds_sst_avhrr-only-v2_[1-2][0-9][0-9][0-9]' + month_str + '.nc')
                    output_dir = '/data/sst/reynolds/decile/1950/monthly/'
                elif product == 'ersst':
                    input_files = glob.glob('/data/sst/ersst/data/monthly_processed/ersst.19[5-9][0-9]' + month_str + '.nc') + \
                                  glob.glob('/data/sst/ersst/data/monthly_processed/ersst.20[0-9][0-9]' + month_str + '.nc')
                    output_dir = '/data/sst/ersst/data/decile/1950/monthly/'
            else:
                if product == 'reynolds':
                    input_files =  glob.glob('/data/sst/reynolds/averages/' + \
                                             avg_period_str + 'monthly/reynolds_sst_avhrr-only-v2_' + \
                                             avg_period_str + 'mthavg_[1-2][0-9][0-9][0-9]' + \
                                             month_str + '_[1-2][0-9][0-9][0-9][0-9][0-9].nc')
                    output_dir = '/data/sst/reynolds/decile/1950/' + avg_period_str + 'monthly/'
                elif product == 'ersst':
                    input_files = glob.glob('/data/sst/ersst/data/averages/' + \
                                            avg_period_str + 'monthly/ersst_v3b_' + \
                                            avg_period_str + 'mthavg_19[5-9][0-9]' + \
                                            month_str + '_[1-2][0-9][0-9][0-9][0-9][0-9].nc') + \
                                  glob.glob('/data/sst/ersst/data/averages/' + \
                                            avg_period_str + 'monthly/ersst_v3b_' + \
                                            avg_period_str + 'mthavg_20[0-9][0-9]' + \
                                            month_str + '_[1-2][0-9][0-9][0-9][0-9][0-9].nc')
                    output_dir = '/data/sst/ersst/data/decile/1950/' + avg_period_str + 'monthly/'
            input_files.sort()
            calc_dec.process(input_files, output_dir, variable_name)