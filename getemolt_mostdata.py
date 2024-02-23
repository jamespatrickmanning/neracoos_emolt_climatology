#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 13:15:36 2024
Routine to determine which non-realtime eMOLT sites have a) lots of years and b) recent years
output  'site', 'lat', 'lon', 'npts', 'nyrs','maxyrs'
@author: JiM

rewritten in Fen 2024 after not finding the original one
usually ran prior to "clim.py" to determine which sites to focus on
"""
import matplotlib.pyplot as plt
import numpy as np
import warnings
import pandas as pd
import netCDF4
import conda 
import os
conda_file_dir = conda.__file__
conda_dir = conda_file_dir.split('lib')[0]
proj_lib = os.path.join(os.path.join(conda_dir, 'share'), 'proj')
from mpl_toolkits.basemap import Basemap
warnings.filterwarnings("ignore")

#HARDCODES
site_lookup='/home/user/emolt_non_realtime/emolt/emolt_site.csv' # has lat/lon for each site

# Now, we get site's lat/lon from a lookup table and then access ERDDAP
def getsite_latlon(df,site):
    # get lat/lon ofr given 4-digit eMOLT site
    df1=df[df['SITE']==site]
    return df1['LAT_DDMM'].values[0],df1['LON_DDMM'].values[0]

def getobs_count_latlon(lat,lon,site='AB01'):
    """
    Function written by Jim Manning to get emolt data from url, return # points
    this version needed in early 2024 when "site" was no longer served via ERDDAP & prepping clim.py
    """
    try:
        print(site)
        url = 'https://comet.nefsc.noaa.gov/erddap/tabledap/eMOLT.csvp?time,depth,sea_water_temperature&latitude='+str(lat)+'&longitude='+str(lon)+'+&orderBy(%22time%22)'
        df=pd.read_csv(url,skiprows=[1])
        npt=len(df)
        df['datet']=pd.to_datetime(df['time (UTC)'])
        maxyr=np.max(df['datet']).year# saves the last year
        nyr=(np.max(df['datet'])-np.min(df['datet'])).days/365
    except:
        npt=0;nyr=0;maxyr=0
    if nyr>10:
        print(lat,lon,site)
    return npt,nyr,maxyr

#Main Code
df=pd.read_csv(site_lookup)
dfout=pd.DataFrame(columns=['site','lat','lon','npts','nyrs'])
site,lat,lon,npts,nyrs,maxyrs=[],[],[],[],[],[]
for k in range(len(df['SITE'])):
    site.append(df['SITE'][k])
    la,lo=getsite_latlon(df,df['SITE'].values[k])
    lat.append(la);lon.append(lo)
    npt,nyr,maxyr=getobs_count_latlon(la,lo,df['SITE'][k])
    npts.append(npt);nyrs.append(nyr);maxyrs.append(maxyr)
dfout['site']=site;dfout['lat']=lat;dfout['lon']=lon;dfout['npts']=npts;dfout['nyrs']=nyrs;dfout['maxyrs']=maxyrs
dfout.to_csv('getemolt_mostdata.csv',index=None)


