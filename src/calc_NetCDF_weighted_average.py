#!/usr/bin/env python
"""
Title: calc_NetCDF_mean.py
Author: Nicholas Summons, n.summons@bom.gov.au
CreationDate: 2012-12-17

Description: 
            Function for calculating weighted average from multiple NetCDF files.
                        
            Input arguments:
                input_files:        List of file names.
                data_var_name:      Name of data variable for averaging.
                output_file:        Output file name.
                global_attributes:  Dictionary containing global attributes for output file.
            
            Note: Time variable will be set to value found in first file processed.
"""
import numpy
import netCDF4
import datetime


def calc_NetCDF_weighted_average(input_files, data_var_names, output_file, scale_factors):
    
    output_file_created = False
    
    for k2, data_var_name in enumerate(data_var_names):
        scale_factor = scale_factors[k2]
        for k, input_file in enumerate(input_files):

            # Open input file
            nc = netCDF4.Dataset(input_file, mode='r')

            data_var = nc.variables[data_var_name]
            data_var_attrs = data_var.ncattrs()

            if output_file_created is False: 

                # Create output file
                nc_out = netCDF4.Dataset(output_file, 'w', format='NETCDF4')
                output_file_created = True

                # Create dimensions by replicating those in input file
                for dimName, dim in nc.dimensions.iteritems():
                    dimLen = len(dim)
                    if dim.isunlimited():
                        dimLen = 0
                    nc_out.createDimension(dimName, dimLen)

                # Create dimension variables and copy values from input file
                for varName in nc.variables.keys():
                    if varName in nc.dimensions.keys():
                        var = nc.variables[varName]
                        var_out = nc_out.createVariable(varName, var.dtype, var.dimensions)
                        for attr in var.ncattrs():
                            if attr == '_FillValue':
                                continue
                            var_out.setncattr(attr, var.getncattr(attr))
                        var_out[:] = var[:]

                # Copy global attributes
                #for attr in global_attributes:
                #    nc_out.setncattr(attr, global_attributes[attr])
                    
                # Copy global attributes
                attdict = nc.__dict__
                attdict['filename'] = unicode(output_file)
                attdict['history'] = datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S %Y") + \
                                    ': Calculated weighted average.' + '\n  ' + \
                                    attdict['history']
                         
                for attr in attdict:
                    nc_out.setncattr(attr, attdict[attr])      

                if 'missing_value' in data_var_attrs:
                    missing_value = data_var.getncattr('missing_value')
                else:
                    missing_value = -999

            if k == 0:
                # Initialise masked array for calculating mean
                sum_array = numpy.ma.zeros(data_var.shape, fill_value=missing_value)

                # Create data variable for storing calculated mean
                data_var_mean = nc_out.createVariable(data_var_name, 'f', data_var.dimensions,
                                                      zlib=True, complevel=6, fill_value=missing_value)
                for attr in data_var_attrs:
                    if attr == '_FillValue':
                        continue
                    data_var_mean.setncattr(attr, data_var.getncattr(attr))

            sum_array += (data_var[:] * float(scale_factor))
            nc.close()

        data_var_mean[:] = sum_array / len(input_files)

    # Save data and close file
    nc_out.sync()
    nc_out.close()
