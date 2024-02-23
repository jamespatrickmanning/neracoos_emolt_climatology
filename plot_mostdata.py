#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 11:25:37 2024
plots the output of "getemolt_mostdata.py"
@author: user
"""
import matplotlib.pyplot as plt
import warnings
import pandas as pd
import netCDF4
import conda 
import numpy as np
import os
conda_file_dir = conda.__file__
conda_dir = conda_file_dir.split('lib')[0]
proj_lib = os.path.join(os.path.join(conda_dir, 'share'), 'proj')
from mpl_toolkits.basemap import Basemap
warnings.filterwarnings("ignore")

#HARDCODES
gbox=[-74.,-66.,35.,45.]
maxnyrs=20 # max number of years to span
url='http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/hindcasts/30yr_gom3'
nc = netCDF4.Dataset(url).variables
lats = nc['lat'][:]
lons = nc['lon'][:]
depths = nc['h'][:] 
depthint=[100.,200.]
mode='isobaths'
yrs=[10,20]
maxyr_criteria=2023 #most recent  year


def make_basemap(gbox,resolution='i'):
    latsize=[gbox[2],gbox[3]]
    lonsize=[gbox[0],gbox[1]]
    '''
    tick_int=gbox[3]-gbox[2] # allow for 3-4 tick axis label intervals
    if (tick_int>=1):
        tick_int=1.   # make the tick_interval integer increments
    elif (tick_int>.5) & (tick_int<1):
        tick_int=.5
    else:
        tick_int=.2
    
    #fig,ax=plt.subplots()
    '''
    #fig = plt.figure(figsize=(8, 6), edgecolor='w')
    m = Basemap(projection='merc',llcrnrlat=min(latsize),urcrnrlat=max(latsize),\
                llcrnrlon=min(lonsize),urcrnrlon=max(lonsize),resolution=resolution)
    m.fillcontinents(color='gray')
    return m

def plot_depth(m,lons,lats,depths,depthint=[100.,200.],mode='fill'):
    # uses FVCOM grid values
    # where "m" is a basemap object
    # where depth int is the depth desired
    ''' the following might be included in main program
    url='http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/hindcasts/30yr_gom3'
    nc = netCDF4.Dataset(url).variables
    lats = nc['lat'][:]
    lons = nc['lon'][:]
    depths = nc['h'][:]  # depth
    '''
    xs,ys=m(lons,lats)
    if mode=='fill':
        plt.tricontourf(xs,ys,depths,[200.,1000.],colors='violet',zorder=0)
    else:
        ax1.tricontour(xs,ys,depths,[200.],linewidths=0.3,linestyles='dashed',zorder=10)

#Main Code
dfout=pd.read_csv('getemolt_mostdata.csv')
fig, ax1 = plt.subplots()

m=make_basemap(gbox)
im1 = m.shadedrelief() # Value stored in a variable to resolve a bug
im1.axes.add_image(im1)
col=['k','r']
for k in range(len(yrs)):
    dfX=dfout[dfout['nyrs']>yrs[k]]
    x,y=m(dfX.lon.values,dfX.lat.values)
    m.scatter(x,y,zorder=0,color=col[k],label='spans >'+str(yrs[k])+' years')
    if k==0:
        bx=(max(x)-min(x))/20.
        by=(max(y)-min(y))/20.
        ax1.set_ylim(min(y)-by,max(y)+by)
        ax1.set_xlim(min(x),max(x)+bx)
        
dfX=dfX[dfX['maxyrs']>=maxyr_criteria]
x,y=m(dfX.lon.values,dfX.lat.values)
m.scatter(x,y,zorder=0,color=col[k],s=90)
for i in range(len(dfX)):
    ax1.annotate(dfX['site'].values[i], (x[i],y[i]),fontsize=6,fontweight='bold', xytext=(10, 0), textcoords='offset points')
ax1.annotate('w/100 & 200 meter isobaths',(np.mean(x)-3*bx,np.min(y)+3*by),fontsize=6,fontweight='bold')
ax1.set_title('non-realtime eMOLT hourly time series')
plt.legend(loc='upper left')
#    ax1.annotate(dfX['site'].values[i], xy=(float(x[i]), float(y[i])), xycoords='data', xytext=(x, y), textcoords='data')
#for j in range(len(dfX)):
#    ax1.text(x[j],y[j],dfX['site'].values[j],size=8,color='w')
#plot_depth(m,lons,lats,depths,mode='isobaths')
xs,ys=m(lons,lats)
ax1.tricontour(xs,ys,depths,[100.,200.],linewidths=0.3,linestyles='dashed',zorder=10,colors=['k','k'])
