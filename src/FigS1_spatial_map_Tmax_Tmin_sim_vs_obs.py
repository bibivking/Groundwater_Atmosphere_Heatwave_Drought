#!/usr/bin/python

'''
Functions:
1. Compare LIS-CABLE with GRACE, GLEAM, & DOLCE
2. GW vs FD
3. plot time-series and spitial (difference) map
'''

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy.feature import NaturalEarthFeature, OCEAN
from scipy.interpolate import griddata
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.ticker as mticker
from convert_units import get_land_var_scale, get_land_var_range_diff
from common_utils import *

def regrid_obs_to_WRF(input_file, WRF_file,var,obs_type):

    filein = Dataset(input_file, mode='r')
    if obs_type == "AWAP":
        lat_in    = filein.variables["latitude"][:]
        lon_in    = filein.variables["longitude"][:]
    if obs_type == "ERAI":
        lat_in    = filein.variables["lat"][:]
        lon_in    = filein.variables["lon"][:]    
    if obs_type == "ERA5":
        lat_in    = filein.variables["latitude"][:]
        lon_in    = filein.variables["longitude"][:]
        
    wrf_file  = Dataset(WRF_file, mode='r')
    lat_out   = wrf_file.variables["XLAT"][0,:,:]
    lon_out   = wrf_file.variables["XLONG"][0,:,:]
    nlat      = len(lat_out[:,0])
    nlon      = len(lon_out[0,:])

    lon_in_2D, lat_in_2D = np.meshgrid(lon_in,lat_in)
    lon_in_1D            = np.reshape(lon_in_2D,-1)
    lat_in_1D            = np.reshape(lat_in_2D,-1)

    # Value                = np.zeros((365,nlat,nlon))
    # print(np.shape(Value))
    #
    # for day in np.arange(365):
    value = np.reshape(var,-1)
    Value = griddata((lon_in_1D, lat_in_1D), value, (lon_out, lat_out), method="linear")

    print("np.shape(Value)")
    print(np.shape(Value))

    return Value

# def regrid_ERAI_to_WRF(ERAI_file, WRF_file,T_erai):
    
#     erai_file = Dataset(ERAI_file, mode='r')
#     lat_in    = erai_file.variables["lat"][:]
#     lon_in    = erai_file.variables["lon"][:]

#     wrf_file  = Dataset(WRF_file, mode='r')
#     lat_out   = wrf_file.variables["XLAT"][0,:,:]
#     lon_out   = wrf_file.variables["XLONG"][0,:,:]
#     nlat      = len(lat_out[:,0])
#     nlon      = len(lon_out[0,:])

#     lon_in_2D, lat_in_2D = np.meshgrid(lon_in,lat_in)
#     lon_in_1D            = np.reshape(lon_in_2D,-1)
#     lat_in_1D            = np.reshape(lat_in_2D,-1)

#     value = np.reshape(t_awap,-1)
#     Value = griddata((lon_in_1D, lat_in_1D), value, (lon_out, lat_out), method="linear")

#     print("np.shape(Value)")
#     print(np.shape(Value))

#     return Value

def plot_spatial_T(case_names, wrf_path, AWAP_file, var_name, message=None):

    # ======================= Make plots ========================
    # Three integers (nrows, ncols, index)

    fig, ax = plt.subplots(nrows=3, ncols=4, figsize=[15,12], sharex=True, sharey=True, squeeze=True,
                           subplot_kw={'projection': ccrs.PlateCarree()})
    plt.subplots_adjust(wspace=-0.3, hspace=0) # left=0.15,right=0.95,top=0.85,bottom=0.05,

    # left = 0.125  # the left side of the subplots of the figure
    # right = 0.9   # the right side of the subplots of the figure
    # bottom = 0.1  # the bottom of the subplots of the figure
    # top = 0.9     # the top of the subplots of the figure
    # wspace = 0.2  # the amount of width reserved for space between subplots,
    #             # expressed as a fraction of the average axis width
    # hspace = 0.2  # the amount of height reserved for space between subplots,
    #             # expressed as a fraction of the average axis height

    plt.rcParams['text.usetex']     = False
    plt.rcParams['font.family']     = "sans-serif"
    plt.rcParams['font.serif']      = "Helvetica"
    plt.rcParams['axes.linewidth']  = 1.5
    plt.rcParams['axes.labelsize']  = 14
    plt.rcParams['font.size']       = 14
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['xtick.labelsize'] = 14
    plt.rcParams['ytick.labelsize'] = 14

    almost_black = '#262626'
    # change the tick colors also to the almost black
    plt.rcParams['ytick.color']     = almost_black
    plt.rcParams['xtick.color']     = almost_black

    # change the text colors also to the almost black
    plt.rcParams['text.color']      = almost_black

    # Change the default axis colors from black to a slightly lighter black,
    # and a little thinner (0.5 instead of 1)
    plt.rcParams['axes.edgecolor']  = almost_black
    plt.rcParams['axes.labelcolor'] = almost_black

    # set the box type of sequence number
    props = dict(boxstyle="round", facecolor='white', alpha=0.0, ec='white')
    # choose colormap

    states= NaturalEarthFeature(category="cultural", scale="50m",
                                        facecolor="none",
                                        name="admin_1_states_provinces_shp")
    # ocean = NaturalEarthFeature('cultural', 'ocean', scale='50m',
    #                             edgecolor='none', facecolor="lightgray")

    # ======================= Set colormap =======================
    cmap       = plt.cm.seismic
    blue2white = truncate_colormap(cmap, minval=0., maxval=0.5)
    white2red  = truncate_colormap(cmap, minval=0.5, maxval=1.)
    cmap       = plt.cm.seismic_r
    red2white  = truncate_colormap(cmap, minval=0., maxval=0.5)
    white2blue = truncate_colormap(cmap, minval=0.5, maxval=1.)
    temp_bar   = plt.cm.coolwarm #seismic
    
    
    # ======================= Read WRF file =======================
    # use WRF output's lat & lon, since LIS output has default value
    wrf = Dataset(wrf_path,  mode='r')
    lon = wrf.variables['XLONG'][0,:,:]
    lat = wrf.variables['XLAT'][0,:,:]

    texts = [ "(a)","(b)","(c)","(d)","(e)","(f)",
              "(g)","(h)","(i)","(j)","(k)","(l)"]

    label_x = ["FD-AWAP","GW-AWAP","ERAI-AWAP","ERA5-AWAP"]#"GW-FD"]
    label_y = ["2009","2013","2019"]
    loc_y   = [0.55,0.5,0.45]

    cnt     = 0

    # ==================== Set up files ====================
    for i, case_name in enumerate(case_names):

        if case_name == "hw2009_3Nov":
            period     = "20090122-20090213"
            time_s = datetime(2009,1,28,0,0,0,0)
            time_e = datetime(2009,2,8,23,59,0,0)
            erai_file = "/g/data/w97/mm3972/scripts/Heatwave/coupled_GW_HW/nc_file/erai/tas_3hrs_ERAI_historical_fc-sfc_20090101_20090228.nc"
            era5_file = "/g/data/w97/mm3972/scripts/Heatwave/coupled_GW_HW/nc_file/era5/2t_era5_oper_sfc_20090101-20090228.nc"
        elif  case_name == "hw2013_3Nov":
            period     = "20121229-20130122"
            time_s = datetime(2013,1,4,0,0,0,0)
            time_e = datetime(2013,1,18,23,59,0,0)
            erai_file = "/g/data/w97/mm3972/scripts/Heatwave/coupled_GW_HW/nc_file/erai/tas_3hrs_ERAI_historical_fc-sfc_20130101_20130131.nc"
            era5_file = "/g/data/w97/mm3972/scripts/Heatwave/coupled_GW_HW/nc_file/era5/2t_era5_oper_sfc_20130101-20130131.nc"
        elif  case_name == "hw2019_3Nov":
            period     = "20190108-20190130"
            time_s = datetime(2019,1,14,0,0,0)
            time_e = datetime(2019,1,26,23,59,0,0)
            erai_file = "/g/data/w97/mm3972/scripts/Heatwave/coupled_GW_HW/nc_file/erai/tas_3hrs_ERAI_historical_fc-sfc_20190101_20190131.nc"
            era5_file = "/g/data/w97/mm3972/scripts/Heatwave/coupled_GW_HW/nc_file/era5/2t_era5_oper_sfc_20190101-20190131.nc"

        cpl_land_file     = '/g/data/w97/mm3972/model/wrf/NUWRF/LISWRF_configs/'+case_name+'/ensemble_avg'

        cpl_land_file_gw  = cpl_land_file + '/LIS.CABLE.'+period+'_gw.nc'  # land output of wrf-cable run
        cpl_land_file_fd  = cpl_land_file + '/LIS.CABLE.'+period+'_fd.nc'  # land output of wrf-cable run

        file_paths        = [cpl_land_file_fd,cpl_land_file_gw]

        # ==================== Read WRF-CABLE file ====================
        # Open the NetCDF4 file (add a directory path if necessary) for reading:
        file1 = Dataset(file_paths[0], mode='r')
        file2 = Dataset(file_paths[1], mode='r')

        Time  = nc.num2date(file1.variables['time'][:],file1.variables['time'].units,
                only_use_cftime_datetimes=False, only_use_python_datetimes=True)
        time  = UTC_to_AEST(Time) - datetime(2000,1,1,0,0,0)

        T1    = file1.variables["Tair_f_inst"][:] # "FD"
        T2    = file2.variables["Tair_f_inst"][:] # "GW"
        if var_name == "tmax":
            t1 = spital_var_max(time,T1,time_s,time_e) -273.15
            t2 = spital_var_max(time,T2,time_s,time_e) -273.15
        else:
            t1 = spital_var_min(time,T1,time_s,time_e) -273.15
            t2 = spital_var_min(time,T2,time_s,time_e) -273.15

        print("Read Sim Done")


        # ==================== Read ERA-Interim file ====================
        obs_type = "ERAI"
        
        erai        = Dataset(erai_file, mode='r')
        Time_erai   = nc.num2date(erai.variables['time'][:],erai.variables['time'].units,
                      only_use_cftime_datetimes=False, only_use_python_datetimes=True)
        time_erai   = UTC_to_AEST(Time_erai) - datetime(2000,1,1,0,0,0)
        
        T_erai      = erai.variables["tas"][:]
        
        if var_name == "tmax":
            t_erai_tmp = spital_var_max(time_erai,T_erai,time_s,time_e) -273.15
        else:
            t_erai_tmp = spital_var_min(time_erai,T_erai,time_s,time_e) -273.15
            
        t_erai = regrid_obs_to_WRF(erai_file, wrf_path,t_erai_tmp,obs_type)
        
        print(" ===== ERAI ===== ")
        print(time_erai)
        print(T_erai)
        print(t_erai)
        print("Read ERA-Interim Done")

        # ==================== Read ERA5 file ====================
        obs_type = "ERA5"
        
        era5        = Dataset(era5_file, mode='r')
        Time_era5   = nc.num2date(era5.variables['time'][:],era5.variables['time'].units,
                      only_use_cftime_datetimes=False, only_use_python_datetimes=True)
        time_era5   = UTC_to_AEST(Time_era5) - datetime(2000,1,1,0,0,0)
        
        T_era5      = era5.variables["t2m"][:]
        
        if var_name == "tmax":
            t_era5_tmp = spital_var_max(time_era5,T_era5,time_s,time_e) - 273.15
        else:
            t_era5_tmp = spital_var_min(time_era5,T_era5,time_s,time_e) - 273.15
            
        t_era5 = regrid_obs_to_WRF(era5_file, wrf_path,t_era5_tmp,obs_type)
        
        print(" ===== ERA5 ===== ")
        print(time_era5)
        print(T_era5)
        print(t_era5)
        print("Read ERA5 Done")
                
        # ==================== Read AWAP file ===================
        obs_type = "AWAP"
        time_awap, T_awap = read_var(AWAP_file, var_name, lat_name="latitude", lon_name="longitude")
        t_awap   = spital_var(time_awap, T_awap, time_s, time_e)
        # awap     = Dataset(AWAP_file,  mode='r')
        # lon_awap = awap.variables['longitude'][:]
        # lat_awap = awap.variables['latitude'][:]

        print(" ===== AWAP ===== ")
        print(time_awap)
        print(T_awap)
        print(t_awap)
        print("Read AWAP Done")

        print(" ===== regrid AWAP ===== ")
        t_regrid = regrid_obs_to_WRF(AWAP_file, wrf_path, t_awap,obs_type)
        
        # ==================== Start to plot ====================
        for j in np.arange(4):

            ax[i,j].coastlines(resolution="50m",linewidth=1)
            ax[i,j].set_extent([130,154.5,-44.5,-20])
            ax[i,j].add_feature(states, linewidth=.5, edgecolor="black")

            # Add gridlines
            gl = ax[i,j].gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color=almost_black, linestyle='--')
            gl.xlabels_top  = False
            gl.ylabels_right= False
            gl.xlines       = False
            gl.ylines       = False
            gl.xlocator     = mticker.FixedLocator([125,130,135,140,145,150,155,160])
            gl.ylocator     = mticker.FixedLocator([-45,-40,-35,-30,-25,-20,-15])
            gl.xformatter   = LONGITUDE_FORMATTER
            gl.yformatter   = LATITUDE_FORMATTER
            gl.xlabel_style = {'size':12, 'color':almost_black}#,'rotation': 90}
            gl.ylabel_style = {'size':12, 'color':almost_black}

            if j == 0:
                gl.ylabels_left   = True
            else:
                gl.ylabels_left   = False
            if i == 2:
                gl.xlabels_bottom = True
            else:
                gl.xlabels_bottom = False

            # set y label
            if j == 0:
                ax[i,j].text(-0.2, loc_y[i], label_y[i], va='bottom', ha='center',
                              rotation='vertical', rotation_mode='anchor',
                              transform=ax[i,j].transAxes)
        '''
        # left - FD
        t1     = np.where(t1>70., np.nan, t1)
        clevs1  = [ 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,43, 44, 45,46,47, 48, 49, 50]
        plot1   = ax[i,0].contourf(lon, lat, t1, levels=clevs1, transform=ccrs.PlateCarree(),cmap=temp_bar,extend='both')
        ax[i,0].text(0.02, 0.15, texts[cnt], transform=ax[i,0].transAxes, fontsize=14, verticalalignment='top', bbox=props)
        ax[i,0].add_feature(OCEAN,edgecolor='none', facecolor="lightgray")

        # middle - GW
        t2     = np.where(t2>70., np.nan, t2)
        clevs2   = [ 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,43, 44, 45,46,47, 48, 49, 50]
        plot2    = ax[i,1].contourf(lon, lat, t2, levels=clevs2, transform=ccrs.PlateCarree(),cmap=temp_bar,extend='both')
        ax[i,1].text(0.02, 0.15, texts[cnt+1], transform=ax[i,1].transAxes, fontsize=14, verticalalignment='top', bbox=props)
        ax[i,1].add_feature(OCEAN,edgecolor='none', facecolor="lightgray")

        # right - AWAP
        clevs3   = [ 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,43, 44, 45,46,47, 48, 49, 50]
        plot3    = ax[i,2].contourf(lon_awap, lat_awap, t_awap, levels=clevs3, transform=ccrs.PlateCarree(),cmap=temp_bar,extend='both') #
        ax[i,2].text(0.02, 0.15, texts[cnt+2], transform=ax[i,2].transAxes, fontsize=14, verticalalignment='top', bbox=props)
        ax[i,2].add_feature(OCEAN,edgecolor='none', facecolor="lightgray")

        '''
        # left, FD-AWAP
        t1     = np.where(t1>70., np.nan, t1)
        clevs1  = [ -4,-3,-2,-1,-0.5,0.5,1,2,3,4 ]
        #[ -5,-4.5,-4,-3.5,-3,-2.5,-2,-1.5,-1,-0.5,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5 ]
        plot1   = ax[i,0].contourf(lon, lat, t1-t_regrid, levels=clevs1, transform=ccrs.PlateCarree(),cmap=temp_bar,extend='both')
        ax[i,0].text(0.02, 0.15, texts[cnt], transform=ax[i,0].transAxes, fontsize=14, verticalalignment='top', bbox=props)
        ax[i,0].add_feature(OCEAN,edgecolor='none', facecolor="white")

        # middle left, GW-AWAP
        t2     = np.where(t2>70., np.nan, t2)
        clevs2   = [ -4,-3,-2,-1,-0.5,0.5,1,2,3,4 ]
        plot2    = ax[i,1].contourf(lon, lat, t2-t_regrid, levels=clevs2, transform=ccrs.PlateCarree(),cmap=temp_bar,extend='both')
        ax[i,1].text(0.02, 0.15, texts[cnt+1], transform=ax[i,1].transAxes, fontsize=14, verticalalignment='top', bbox=props)
        ax[i,1].add_feature(OCEAN,edgecolor='none', facecolor="white")

        # middle right, ERAI - AWAP
        t_erai   = np.where(t_erai>70., np.nan, t_erai)
        clevs3   = [ -4,-3,-2,-1,-0.5,0.5,1,2,3,4 ]
        plot3    = ax[i,2].contourf(lon, lat, t_erai-t_regrid, levels=clevs3, transform=ccrs.PlateCarree(),cmap=temp_bar,extend='both')
        ax[i,2].text(0.02, 0.15, texts[cnt+2], transform=ax[i,2].transAxes, fontsize=14, verticalalignment='top', bbox=props)
        ax[i,2].add_feature(OCEAN,edgecolor='none', facecolor="white")
        
        # # right, GW-FD
        # clevs4   = [ -4,-3,-2,-1,-0.5,0.5,1,2,3,4 ]
        # plot4    = ax[i,3].contourf(lon, lat, t2-t1, levels=clevs4, transform=ccrs.PlateCarree(),cmap=temp_bar,extend='both') #
        # ax[i,3].text(0.02, 0.15, texts[cnt+3], transform=ax[i,3].transAxes, fontsize=14, verticalalignment='top', bbox=props)
        # ax[i,3].add_feature(OCEAN,edgecolor='none', facecolor="lightgray")

        # right, ERA5-AWAP
        clevs4   = [ -4,-3,-2,-1,-0.5,0.5,1,2,3,4 ]
        plot4    = ax[i,3].contourf(lon, lat, t_era5-t_regrid, levels=clevs4, transform=ccrs.PlateCarree(),cmap=temp_bar,extend='both') #
        ax[i,3].text(0.02, 0.15, texts[cnt+3], transform=ax[i,3].transAxes, fontsize=14, verticalalignment='top', bbox=props)
        ax[i,3].add_feature(OCEAN,edgecolor='none', facecolor="white")

        # set top x label
        if i == 0:
            # ax[i,0].xaxis.set_label_position('top')
            # ax[i,1].xaxis.set_label_position('top')
            # ax[i,2].xaxis.set_label_position('top')
            # ax[i,0].set_xlabel(label_x[0],labelpad=-0.1)#, fontsize=12)
            # ax[i,1].set_xlabel(label_x[1],labelpad=-0.1)#, fontsize=12)
            # ax[i,2].set_xlabel(label_x[2],labelpad=-0.1)#, fontsize=12)

            ax[i,0].set_title(label_x[0])#, fontsize=12)
            ax[i,1].set_title(label_x[1])#, fontsize=12)
            ax[i,2].set_title(label_x[2])#, fontsize=12)
            ax[i,3].set_title(label_x[3])#, fontsize=12)


        # set bottom colorbar
        if i == 2:

            # left, FD-AWAP
            cbar = plt.colorbar(plot1, ax=ax[:,0], ticklocation="right", pad=0.03, orientation="horizontal",
                                aspect=20, shrink=0.6)
            color_label= "$\mathregular{^o}$C"
            cbar.set_label(color_label, loc='center',size=12)
            cbar.ax.tick_params(labelsize=10, rotation=45)

            # middle left, GW-AWAP
            cbar = plt.colorbar(plot2, ax=ax[:,1], ticklocation="right", pad=0.03, orientation="horizontal",
                                aspect=20, shrink=0.6)
            color_label= "$\mathregular{^o}$C"
            cbar.set_label(color_label, loc='center',size=12)
            cbar.ax.tick_params(labelsize=10, rotation=45)

            # middle right, ERAI-AWAP
            cbar = plt.colorbar(plot3, ax=ax[:,2], ticklocation="right", pad=0.03, orientation="horizontal",
                                aspect=20, shrink=0.6)
            color_label= "$\mathregular{^o}$C"
            cbar.set_label(color_label, loc='center',size=12)
            cbar.ax.tick_params(labelsize=10, rotation=45)
            
            # middle right, GW-FW
            cbar = plt.colorbar(plot4, ax=ax[:,3], ticklocation="right", pad=0.03, orientation="horizontal",
                                aspect=20, shrink=0.6)
            color_label= "$\mathregular{^o}$C"
            cbar.set_label(color_label, loc='center',size=12)
            cbar.ax.tick_params(labelsize=10, rotation=45)
        cnt = cnt + 4
    # plt.tight_layout(pad=0.01)
    # plt.savefig('./plots/FigS1_spatial_map_difference_'+var_name+'_FD_GW_AWAP_ERAI_2009_2013_2019.png',dpi=300,
    #             bbox_inches='tight', pad_inches=0.1)
    plt.savefig('./plots/FigS1_spatial_map_difference_'+var_name+'_FD_GW_AWAP_ERAI_ERA5_2009_2013_2019.png',dpi=300,
                bbox_inches='tight', pad_inches=0.1)
    
    
if __name__ == "__main__":

    # #######################
    #     path setting      #
    # #######################
    AWAP_tmax  = "/g/data/w97/W35_GDATA_MOVED/Shared_data/Observations/AWAP_all_variables/daily/tmax/AWAP_daily_tmax_1970_2019.nc"
    AWAP_tmin  = "/g/data/w97/W35_GDATA_MOVED/Shared_data/Observations/AWAP_all_variables/daily/tmin/AWAP_daily_tmin_1970_2019.nc"
    wrf_path   = "/g/data/w97/mm3972/model/wrf/NUWRF/LISWRF_configs/hw2009_3Nov/ensemble_avg/wrfout_20090122-20090213_gw"
    case_names = ["hw2009_3Nov", "hw2013_3Nov", "hw2019_3Nov"]
    var_name   = "tmax"
    plot_spatial_T(case_names,wrf_path, AWAP_tmax, var_name)
