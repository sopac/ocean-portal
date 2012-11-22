#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Nick Summons <n.summons@bom.gov.au>
#          Elisabeth Thompson <e.thompson@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import math
import bisect
import pdb
import datetime

import netCDF4
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea

from ocean.netcdf.plotter import getCopyright, get_tick_values, discrete_cmap
from ocean.util.pngcrush import pngcrush

def load_BRAN_data(input_data_file, var_name, lat_min, lat_max, lon_min, lon_max, depth_min=0, depth_max=0):

    # Open file
    nc = netCDF4.Dataset(input_data_file)

    if var_name == 'eta':
        if 'eta' not in nc.variables:
            var_name = 'eta_t'

    dimensions = nc.variables[var_name].dimensions

    # Load lat/lon values
    if ('xt_ocean' in dimensions) and ('yt_ocean' in dimensions):
        lons = nc.variables['xt_ocean'][:]
        lats = nc.variables['yt_ocean'][:]
    elif ('xu_ocean' in dimensions) and ('yu_ocean' in dimensions):
        lons = nc.variables['xu_ocean'][:]
        lats = nc.variables['yu_ocean'][:]
    if 'zt_ocean' in dimensions:
        depth = nc.variables['zt_ocean'][:]
    else:
        depth = [0.]
            
    # Subset dimensions
    lat_idx1, lat_idx2 = get_subset_idxs(lats, lat_min, lat_max)
    lon_idx1, lon_idx2 = get_subset_idxs(lons, lon_min, lon_max)
    zlevel_idx1, zlevel_idx2 = get_subset_idxs(depth, abs(depth_min), abs(depth_max))
    lons = lons[lon_idx1:lon_idx2]
    lats = lats[lat_idx1:lat_idx2]
    zlevels = depth[zlevel_idx1:zlevel_idx2]
    
    # Load data
    if len(dimensions) == 4:
        data = nc.variables[var_name][0, zlevel_idx1:zlevel_idx2, lat_idx1:lat_idx2, lon_idx1:lon_idx2]
    else:
        data = nc.variables[var_name][0, lat_idx1:lat_idx2, lon_idx1:lon_idx2]
    
    # Close file
    nc.close()

    # Remove single dimensions from array
    data = np.squeeze(data)
    
    return lats, lons, zlevels, data

def plot_BRAN_depth_slice(depths, lats, lons, zonal_data, meridional_data, lats_all, lons_all, data_sf,
                          lat_cnt, lon_cnt, output_filename='noname.png', title='', units='m/s',
                          cb_ticks=None, cb_tick_fmt="%.0f", cmp_name='jet', proj='cyl',
                          product_label_str=None):
    fg = plt.figure()
    gs = mpl.gridspec.GridSpec(2,5)
    ax1=plt.subplot(gs[1,0:2])
        
    n_colours = cb_ticks.size - 1
    d_cmap = discrete_cmap(cmp_name, n_colours)
    
    # Draw contour
    x, y = np.meshgrid(lons, depths)
    ctr = plt.contour(x, y, zonal_data, levels=cb_ticks, colors='k', linewidths=0.4)
    plt.clabel(ctr, inline=True, fmt=cb_tick_fmt, fontsize=8)

    lons2 = get_grid_edges(lons)
    depths2 = get_grid_edges(depths)
        
    # Plot data
    x2, y2 = np.meshgrid(lons2, depths2)
    img = plt.pcolormesh(x2, y2, zonal_data, shading='flat', cmap=d_cmap, vmin=cb_ticks.min(), vmax=cb_ticks.max())
    
    ax = plt.gca()
    ax.set_ylim(0,300)
    ax.set_ylim(ax.get_ylim()[::-1]) 
    ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(format_longitude))
    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=9)

    plt.ylabel("Depth (m)", fontsize=10)
    plt.xlabel("Longitude", fontsize=10)
    plt.subplots_adjust(right=1.0)
    ax2=plt.subplot(gs[1,2:4])

    # Draw contour
    x, y = np.meshgrid(lats, depths)
    ctr = plt.contour(x, y, meridional_data, levels=cb_ticks, colors='k', linewidths=0.4)
    plt.clabel(ctr, inline=True, fmt=cb_tick_fmt, fontsize=8)

    lats2 = get_grid_edges(lats)
    depths2 = get_grid_edges(depths)
        
    # Plot data
    x2, y2 = np.meshgrid(lats2, depths2)
    img = plt.pcolormesh(x2, y2, meridional_data, shading='flat', cmap=d_cmap, vmin=cb_ticks.min(), vmax=cb_ticks.max())
        
    ax = plt.gca()
    ax.set_ylim(0,300)
    ax.set_ylim(ax.get_ylim()[::-1])
    ax.set_yticklabels([''])
    ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(format_latitude))
    ax.tick_params(axis='x', labelsize=8)
    
    plt.xlabel("Latitude", fontsize=10)
    
    ax3=plt.subplot(gs[0,:-1])

    lat_min = lats[0] - 5.0
    lat_max = lats[-1] + 5.0
    lon_min = lons[0] - 20.0
    lon_max = lons[-1] + 20.0
    
    m = Basemap(projection=proj, llcrnrlat=lat_min, llcrnrlon=lon_min, \
                urcrnrlat=lat_max, urcrnrlon=lon_max, resolution='h')
    m.drawcoastlines(linewidth=0.5, zorder=8, color='#505050')
    m.fillcontinents(color='#F1EBB7', zorder=7)
    plt.hold(True)
    plt.plot([lon_cnt,lon_cnt],[lats[0],lats[-1]], color='k', linestyle='--', linewidth=2, zorder=8)
    plt.plot([lons[0],lons[-1]],[lat_cnt,lat_cnt], color='k', linestyle='--', linewidth=2, zorder=8)
    
    # Convert centre lat/lons to corner values required for pcolormesh
    lons2 = get_grid_edges(lons_all)
    lats2 = get_grid_edges(lats_all)
        
    # Plot data
    x2, y2 = m(*np.meshgrid(lons2, lats2))
    img = m.pcolormesh(x2, y2, data_sf, shading='flat', cmap=d_cmap, vmin=cb_ticks.min(), vmax=cb_ticks.max())
    plt.title(title, fontsize=12)
    
    parallels, p_dec_places = get_tick_values(lat_min, lat_max, 3)
    meridians, m_dec_places = get_tick_values(lon_min, lon_max)
    m.drawparallels(parallels, labels=[True, False, False, False], fmt='%.' + str(p_dec_places) + 'f', 
                    fontsize=8, dashes=[3, 3], color='gray')
    m.drawmeridians(meridians, labels=[False, False, False, True], fmt='%.' + str(m_dec_places) + 'f',
                    fontsize=8, dashes=[3, 3], color='gray')
    cbaxes = fg.add_axes([0.85, 0.15, 0.03, 0.7]) # setup colorbar axes.
    
    cb = fg.colorbar(img, spacing='proportional', drawedges='True', cax=cbaxes,orientation='vertical',
                     extend='both', ticks=cb_ticks)
    cb.set_ticklabels([cb_tick_fmt % k for k in cb_ticks])
    cb.set_label(units)
    
    box = TextArea(getCopyright(), textprops=dict(color='k', fontsize=6))
    copyrightBox = AnchoredOffsetbox(loc=3, child=box, bbox_to_anchor=(-1.3, -0.45), frameon=False, bbox_transform=ax.transAxes)
    ax.add_artist(copyrightBox)

    box = TextArea(product_label_str, textprops=dict(color='k', fontsize=8))
    copyrightBox = AnchoredOffsetbox(loc=4, child=box, bbox_to_anchor=(1.4, -0.45), frameon=False, bbox_transform=ax.transAxes)
    ax.add_artist(copyrightBox)
    
    plt.savefig(output_filename, dpi=150, bbox_inches='tight', pad_inches=1.)
    plt.close()
    
    pngcrush(output_filename)

    return

def get_subset_idxs(x, x_min, x_max):

    if x_min == x_max:
        closest_idx = np.abs(np.array(x) - x_min).argmin()
        return closest_idx, closest_idx + 1

    # assuming that x is sorted, find indexes to the left of x_min and the
    # right of x_max
    start_idx = bisect.bisect_left(x, x_min)
    end_idx = bisect.bisect_right(x, x_max)

    return start_idx, end_idx

def get_grid_edges(x):
    x = np.array(x)
    cntrs = (x[1:] + x[0:-1]) / 2.0
    edges_strt = 2*x[0] - cntrs[0]
    edges_end = 2*x[-1] - cntrs[-1]
    edges = np.append(edges_strt, cntrs)
    edges = np.append(edges, edges_end)
    return edges

def get_vector_plot_settings(lat_min, lat_max, lon_min, lon_max):
    lat_extent = lat_max - lat_min
    lon_extent = lon_max - lon_min
    max_extent = max(lat_extent, lon_extent)
    if max_extent >= 80:
        draw_every = None
        arrow_scale = None
    elif (max_extent >= 60) and (max_extent < 80):
        draw_every = 10
        arrow_scale = 20
    elif (max_extent >= 20) and (max_extent < 60):
        draw_every = 5
        arrow_scale = 15
    elif (max_extent >= 10) and (max_extent < 20):
        draw_every = 5
        arrow_scale = 10
    elif (max_extent >= 7) and (max_extent < 10):
        draw_every = 4
        arrow_scale = 5
    elif (max_extent >= 4) and (max_extent < 7):
        draw_every = 3
        arrow_scale = 5
    else:
        draw_every = 1
        arrow_scale = 5
    return draw_every, arrow_scale

def format_longitude(x, pos=None):
    x = np.mod(x + 180, 360) - 180
    if x==-180:
        return u"{0:.0f}\u00B0".format(abs(x))
    elif x<0:
        return u"{0:.0f}\u00B0W".format(abs(x))
    else:
        return u"{0:.0f}\u00B0E".format(x)

def format_latitude(y, pos=None):
    if y<0:
        return u"{0:.0f}\u00B0S".format(abs(y))
    elif y>0:
        return u"{0:.0f}\u00B0N".format(y)
    else:
        return u"{0:.0f}\u00B0".format(y)
