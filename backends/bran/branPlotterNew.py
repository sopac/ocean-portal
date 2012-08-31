import netCDF4
import math
import numpy as np
import pdb
from mpl_toolkits.basemap import Basemap
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea
import matplotlib as mpl
import matplotlib.pyplot as plt
import pylab as py
import datetime


def load_BRAN_data(input_data_file, var_name, lat_min, lat_max, lon_min, lon_max, depth_min=0, depth_max=0):

    # Open file
    nc = netCDF4.Dataset(input_data_file)

    if var_name == 'eta':
        if 'eta' not in nc.variables:
            var_name = 'eta_t'

    dimensions = nc.variables[var_name].dimensions

    # Load lat/lon values
    if ('xt_ocean' in dimensions) & ('yt_ocean' in dimensions):
        lons = nc.variables['xt_ocean'][:]
        lats = nc.variables['yt_ocean'][:]
    elif ('xu_ocean' in dimensions) & ('yu_ocean' in dimensions):
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
    lons = lons[lon_idx1:lon_idx2 + 1]
    lats = lats[lat_idx1:lat_idx2 + 1]
    zlevels = depth[zlevel_idx1:zlevel_idx2 + 1]
    
    # Load data
    if len(dimensions) == 4:
        data = nc.variables[var_name][0, zlevel_idx1:zlevel_idx2+1, lat_idx1:lat_idx2+1, lon_idx1:lon_idx2+1]
    else:
        data = nc.variables[var_name][0, lat_idx1:lat_idx2+1, lon_idx1:lon_idx2+1]
    
    # Close file
    nc.close()

    # Remove single dimensions from array
    data = np.squeeze(data)
    
    return lats, lons, zlevels, data


def plot_BRAN_surface_data(lats, lons, data, lat_min, lat_max, lon_min, lon_max,
                           output_filename='noname.png', title='', units='m/s',
                           cb_ticks=None, cb_tick_fmt="%.0f", cmp_name='jet', 
                           contourLines=False, proj='cyl', product_label_str=None,
                           vlat=None, vlon=None, u=None, v=None):

    m = Basemap(projection=proj, llcrnrlat=lat_min, llcrnrlon=lon_min, \
                urcrnrlat=lat_max, urcrnrlon=lon_max, resolution='h')
    
    # Create colormap
    if cb_ticks is None:
        cb_ticks,junk = get_tick_values(data.min(), data.max(), 6, 12)
    n_colours = cb_ticks.size - 1
    d_cmap = discrete_cmap(cmp_name, n_colours)
    
    # Draw contour
    if contourLines:
        x, y = m(*np.meshgrid(lons, lats))
        ctr = m.contour(x, y, data, levels=cb_ticks, colors='k', linewidths=0.4)
        plt.clabel(ctr, inline=True, fmt=cb_tick_fmt, fontsize=8)

    # Convert centre lat/lons to corner values required for pcolormesh
    lons2 = get_grid_edges(lons)
    lats2 = get_grid_edges(lats)
        
    # Plot data
    x2, y2 = m(*np.meshgrid(lons2, lats2))
    img = m.pcolormesh(x2, y2, data, shading='flat', cmap=d_cmap, vmin=cb_ticks.min(), vmax=cb_ticks.max())
    ax = plt.gca()
    
    if (u is not None) & (v is not None) & (vlat is not None) & (vlon is not None):
        # Draw vectors
        draw_every, arrow_scale = get_vector_plot_settings(lat_min, lat_max, lon_min, lon_max)
        draw_vector_plot(m, vlon, vlat, u, v, draw_every=draw_every, arrow_scale=arrow_scale)
        
    # Draw colorbar    
    cb = py.colorbar(img, shrink=0.8, spacing='proportional', drawedges='True', orientation='vertical', 
                     extend='both', ticks=cb_ticks)
    cb.set_ticklabels([cb_tick_fmt % k for k in cb_ticks])
    cb.set_label(units)
        
    m.drawcoastlines(linewidth=0.1, zorder=6)
    m.fillcontinents(color='#cccccc', zorder=7)

    parallels, p_dec_places = get_tick_values(lat_min, lat_max)
    meridians, m_dec_places = get_tick_values(lon_min, lon_max)
    m.drawparallels(parallels, labels=[True, False, False, False], fmt='%.' + str(p_dec_places) + 'f', 
                    fontsize=8, dashes=[3, 3], color='gray')
    m.drawmeridians(meridians, labels=[False, False, False, True], fmt='%.' + str(m_dec_places) + 'f',
                    fontsize=8, dashes=[3, 3], color='gray')
    plt.title(title, fontsize=10)
    
    box = TextArea(getCopyright(), textprops=dict(color='k', fontsize=6))
    copyrightBox = AnchoredOffsetbox(loc=3, child=box, bbox_to_anchor=(-0.1, -0.15), frameon=False, bbox_transform=ax.transAxes)
    ax.add_artist(copyrightBox)
    
    if product_label_str is not None:
        box = TextArea(product_label_str, textprops=dict(color='k', fontsize=8))
        copyrightBox = AnchoredOffsetbox(loc=4, child=box, bbox_to_anchor=(1.040, -0.15), frameon=False, bbox_transform=ax.transAxes)
        ax.add_artist(copyrightBox)
        
    plt.savefig(output_filename, dpi=150, bbox_inches='tight', pad_inches=1.)
    plt.close()
    
    return m


def plot_BRAN_depth_slice(depths, lats, lons, zonal_data, meridional_data,
                          output_filename='noname.png', title='', units='m/s',
                          cb_ticks=None, cb_tick_fmt="%.0f", cmp_name='jet', 
                          product_label_str=None):
    fg = py.figure()
    
    gs = mpl.gridspec.GridSpec(8,6)
    ax1=py.subplot(gs[1:4,:-1])
        
    n_colours = cb_ticks.size - 1
    d_cmap = discrete_cmap(cmp_name, n_colours)
    
    # Draw contour
    x, y = np.meshgrid(lons, depths)
    ctr = py.contour(x, y, zonal_data, levels=cb_ticks, colors='k', linewidths=0.4)
    plt.clabel(ctr, inline=True, fmt=cb_tick_fmt, fontsize=8)

    lons2 = get_grid_edges(lons)
    depths2 = get_grid_edges(depths)
        
    # Plot data
    x2, y2 = np.meshgrid(lons2, depths2)
    img = py.pcolormesh(x2, y2, zonal_data, shading='flat', cmap=d_cmap, vmin=cb_ticks.min(), vmax=cb_ticks.max())
    plt.title(title, fontsize=12)
    
    ax = plt.gca()
    ax.set_ylim(0,300)
    ax.set_ylim(ax.get_ylim()[::-1]) 

    py.ylabel("Depth (m)", fontsize=10)
    py.xlabel("Longitude", fontsize=10)
    
    ax2=py.subplot(gs[5:8,:-1])

    # Draw contour
    x, y = np.meshgrid(lats, depths)
    ctr = py.contour(x, y, meridional_data, levels=cb_ticks, colors='k', linewidths=0.4)
    plt.clabel(ctr, inline=True, fmt=cb_tick_fmt, fontsize=8)

    lats2 = get_grid_edges(lats)
    depths2 = get_grid_edges(depths)
        
    # Plot data
    x2, y2 = np.meshgrid(lats2, depths2)
    img = py.pcolormesh(x2, y2, meridional_data, shading='flat', cmap=d_cmap, vmin=cb_ticks.min(), vmax=cb_ticks.max())

    ax = plt.gca()
    ax.set_ylim(0,300)
    ax.set_ylim(ax.get_ylim()[::-1]) 

    py.ylabel("Depth (m)", fontsize=10)
    py.xlabel("Latitude", fontsize=10)
    
    cbaxes = fg.add_axes([0.8, 0.1, 0.03, 0.7]) # setup colorbar axes.
    cb = fg.colorbar(img, spacing='proportional', drawedges='True', cax=cbaxes,orientation='vertical',
                       extend='both', ticks=cb_ticks)
    cb.set_ticklabels([cb_tick_fmt % k for k in cb_ticks])
    cb.set_label(units)
    
    box = TextArea(getCopyright(), textprops=dict(color='k', fontsize=6))
    copyrightBox = AnchoredOffsetbox(loc=3, child=box, bbox_to_anchor=(-0.1, -0.45), frameon=False, bbox_transform=ax.transAxes)
    ax.add_artist(copyrightBox)

    box = TextArea(product_label_str, textprops=dict(color='k', fontsize=8))
    copyrightBox = AnchoredOffsetbox(loc=4, child=box, bbox_to_anchor=(1.040, -0.45), frameon=False, bbox_transform=ax.transAxes)
    ax.add_artist(copyrightBox)
    
    plt.savefig(output_filename, dpi=150, bbox_inches='tight', pad_inches=1.)
    plt.close()
    
    return


def draw_vector_plot(m, x, y, u, v, draw_every=1, arrow_scale=10, quiverkey_value=0.5, units='ms^{-1}', 
                     quiverkey_xpos=0.25, quiverkey_ypos=0.28):
    # Draw vector plot
    #
    # Input arguments:
    # ----------------
    #   x, y            -> x, y (or lon, lat) values
    #   u, v            -> vector components (i.e. Vx, Vy)
    #   draw_every      -> draw every nth arrow
    #   arrow_scale     -> scale arrow size
    #   quiverkey_value -> Quiver key value
    #   units           -> Units for quiver key label
    #   quiverkey_xpos  -> x position of quiver key
    #   quiverkey_ypos  -> y position of quiver key
    x = x[::draw_every]
    y = y[::draw_every]
    u = u[::draw_every,::draw_every]
    v = v[::draw_every,::draw_every]
    x, y = m(*np.meshgrid(x, y))
    q = m.quiver(x, y, u, v, pivot='mid', scale=arrow_scale,
                  minshaft=1, minlength=0.85, headlength=2.5, headaxislength=2.5)
    quiverkey_label = '$' + str(quiverkey_value) + units + '$'
    py.quiverkey(q, quiverkey_xpos, quiverkey_ypos, quiverkey_value, quiverkey_label, coordinates='figure', 
                 labelpos='N', labelsep=0.01, fontproperties={'size':'xx-small', 'weight':'1000'})

def get_subset_idxs(x, x_min, x_max):
    valid_idxs = [i for i,x_i in enumerate(x) if (x_i >= x_min) & (x_i <= x_max)]
    if len(valid_idxs) > 0:
        start_idx = valid_idxs[0]
        end_idx = valid_idxs[-1]
    elif x_min == x_max:
        closest_idx = np.abs(np.array(x) - x_min).argmin()
        start_idx = closest_idx
        end_idx = closest_idx
    else:
        start_idx = None
        end_idx = None
    return start_idx, end_idx

def get_tick_values(x_min, x_max, min_ticks=4, max_ticks=9):
    """
    Automatically determine best latitude / longitude tick values for plotting.

    Input arguments:
        x_min       Minimum lat/lon value
        x_max       Maximum lat/lon value
        min_ticks   Minimum number of ticks
        max_ticks   Maximum number of ticks    

    Example usage: 
        get_tick_values(-30,30) -> [-30., -20., -10., 0., 10., 20., 30.]
    """
    eps = 0.0001
    
    # Calculate base 10 exponent of the value range
    dif_exp = np.floor(np.log10(x_max - x_min))
    
    for k in [1.0,0.5,0.2]:
        test_interval = math.pow(10, dif_exp) * k
        start_value = np.ceil(x_min/test_interval)*test_interval
        ticks = np.arange(start_value, x_max + eps, test_interval)
        if (ticks.size >= min_ticks) & (ticks.size <= max_ticks):
            break
    
    # Determine number of decimal places required for labels
    if dif_exp <= 0:
        if k >= 1.0:
            dec_places = abs(dif_exp)
        else:
            dec_places = abs(dif_exp) + 1
    else:
        dec_places = 0
    
    return ticks, int(dec_places)

def discrete_cmap(cmap_name, n_colours):
    cmap = mpl.cm.get_cmap(cmap_name, n_colours)
    clrs = cmap(range(0, n_colours))
    return mpl.colors.ListedColormap(clrs)

def getCopyright():
    return ur'\u00A9' + "Commonwealth of Australia "\
           + datetime.date.today().strftime('%Y')\
           + "\nAustralian Bureau of Meteorology, COSPPac COMP"

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
    if max_extent >= 60:
        draw_every = 10
        arrow_scale = 20
    elif (max_extent >= 20) & (max_extent < 60):
        draw_every = 5
        arrow_scale = 15
    elif (max_extent >= 10) & (max_extent < 20):
        draw_every = 5
        arrow_scale = 10
    elif (max_extent >= 7) & (max_extent < 10):
        draw_every = 4
        arrow_scale = 5
    elif (max_extent >= 4) & (max_extent < 7):
        draw_every = 3
        arrow_scale = 5
    else:
        draw_every = 1
        arrow_scale = 5
    return draw_every, arrow_scale
