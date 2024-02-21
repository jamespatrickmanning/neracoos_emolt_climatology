# -*- coding: utf-8 -*-
"""
Read an eMOLT data from ERDDAP 
and generate climatology files (daily, weekly, etc for NERACOOS)
    
Created on Sun Nov 18 2012
Modified August 2014 to read new ERDDAP archive
Modified December 2015 to clean it up, added comments, etc.
Modified December 2017 to fix "getdata_eric" functions
Modified August 2018 to make cleaner csv files
Modified March 2019 to be compatible with the ERDDAP server and added function within this code
Modified Feb 2024 to deal with:
    a) sites not being part of ERDDAP
    b) Python 3+ needs including print, resample, ix vs loc,
    c) 80% of max count needed for annual mean
@author: JiM
"""
#### HARDCODES ################################################################################################################
#site=['WD01','CP01','AB01','JC01','BD01','BI01','MM01','BC01','BI02','BF01','BM02','NL01','ET01','KO01','JS02','BM01','JS06',\
#'DMF1','DMF6','DJ01','DMF5','BA03','NARR','BN01','DMF7','DMF4','DMF2','WHAQ','AG01','BA02','BA01'] # all the sites w/lot of data
#site=['BC01','BD01','BN01','DJ01','JT04','WD01'] # sites of interest where BC01,BD01,BN01,DJ01,JT04,MM01,WD01 are already on NERACOOS
#site=['DMF1','DMF2','DMF3','DMF4','DMF5','DMF6','DMF7','DMF8','DMF9','MA10','MA11'] # sites contributed by DMF
#site=['BD01','BN01','DJ01','JT04'] # sites updated in 2016
#site=['WHAQ'] # sites specifically requested by Narr Bay Folks in Dec 2016
site=['CP01','JC01','BI01','BC01','BI02','BF01','JS02','JS06','BN01','AG01','JT04','AC02'] #sites for NERACOOS in 2024      
site_lookup='/home/user/emolt_non_realtime/emolt/emolt_site.csv' # has lat/lon for each site

#outdir='/net/pubweb_html/epd/ocean/MainPage/lob/' #this is where I stored the output files and plots on my network
outdir='./output/' #this is where I stored the output files and plots on my network
pltdir='./plots/'

numperday=24 # standard samples per day
numperdayDMF=12    # had to use this in the DMF case since they typically only record every two hours
minnumperday=18    # minimum number of observations to generate daily average (since most have numperday =24)
minnumperdayDMF=10 # had to use this in DMF case since they typically only record every two hours
mindayspermonth=25  # we use this criteria according to NERACOOS convention
minsamperyear=8000  # we use this criteria as "12" when feeding to NARR BAY group WHAQ and NARR data since we only had monthly data in some years
###################################################################################################################################

### IMPORT MODULES
from pandas import Series
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import numpy as np
from pandas import read_csv,DataFrame
from dateutil.parser import parse
import warnings
warnings.filterwarnings("ignore")

# We onced had a function to read eMOLT data given 4-digit site code and time wanted (obsolete in 2023 when "site" was removed from ERDDAP)
# Now, we get site's lat/lon from a lookup table and then access ERDDAP

def getsite_latlon(site):
    # get lat/lon ofr given 4-digit eMOLT site
    df=read_csv(site_lookup)
    df1=df[df['SITE']==site]
    return df1['LAT_DDMM'].values[0],df1['LON_DDMM'].values[0]

def getobs_tempdepth_latlon(lat,lon):
    """
    Function written by Jim Manning to get emolt data from url, return datetime, depth, and temperature.
    this version needed in early 2023 when "site" was no longer served via ERDDAP
    """
    url = 'https://comet.nefsc.noaa.gov/erddap/tabledap/eMOLT.csvp?time,depth,sea_water_temperature&latitude='+str(lat)+'&longitude='+str(lon)+'+&orderBy(%22time%22)'
    df=read_csv(url,skiprows=[1])
    df['time']=df['time (UTC)']
    temp=1.8 * df['sea_water_temperature (degree_C)'].values + 32 #converts to degF
    depth=df['depth (m)'].values
    time=[];
    for k in range(len(df)):
            time.append(parse(df.time[k]))
    print('using erddap')            
    dfnew=DataFrame({'temp':temp,'Depth':depth},index=time)
    return dfnew

### MAIN PROGRAM LOOP THROUGH SITES
for k in range(len(site)):
    # get data from ERDDAP using a function in the "getdata_eric" module of functions
    if (site[k][0:3]=='DMF') or (site[k][0:3]=='MA1'): #non-standard case 
        minnumperday=minnumperdayDMF# had to use this in DMF case since they typically only record every two hours
        numperday=numperdayDMF
    print('getting data for '+site[k]+' on NEFSC ERDDAP server')
    [lat,lon]=getsite_latlon(site[k])# started using this on 25 May 2023 when NEFSC took away "site" from ERDDAP
    df=getobs_tempdepth_latlon(lat,lon)
    #[datet,temp,depth_i]=getobs_temp(site[k],input_time=[dt.datetime(1880,1,1,0,0,0,0,pytz.UTC),dt.datetime(2020,1,1,0,0,0,0,pytz.UTC)])
    depth=int(np.mean(df.Depth))# mean depth of instrument to be added to outputfilename (NOTE: WE MAY NEED TO CHANGE THIS FOR SITES WITH MORE THAN JUST BOTTOM RECORDS.)
    temp=df.temp.values
    datet=df.index.values
    tso=Series(temp,index=datet)

    #create a daily mean
    #tsod=tso.resample('D',how=['count','mean','median','min','max','std'],loffset=timedelta(hours=-12)) #old method to create daily averages
    tsod=tso.resample('D').agg({'count':np.size, 'mean':np.mean,'median':np.median,'min':np.min,'max':np.max,'std':np.std})
    #tsod.ix[tsod['count']<minnumperday,['mean','median','min','max','std']] = 'NaN' # set daily averages to not-a-number if not enough went into it
    tsod.loc[tsod['count']<minnumperday,['mean','median','min','max','std']] = 'NaN' # set daily averages to not-a-number if not enough went into it
    #add columns for custom date format
    tsod['yy']=tsod.index.year
    tsod['mm']=tsod.index.month
    tsod['dd']=tsod.index.day
    tsod['mean']=tsod['mean'].astype(float)   # makes for cleaner format on output to csv
    tsod['std']=tsod['std'].astype(float)   # makes for cleaner format on output to csv
    output_fmt=['yy','mm','dd','count','mean','median','min','max','std']
    tsodp=tsod.reindex(columns=output_fmt)  
    tsodp.to_csv(outdir+site[k]+'_wtmp_da_'+str(depth)+'.csv',index=False,header=False,na_rep='NaN',float_format='%10.2f')

    #create a monthly mean
    tsom=tso.resample('m',kind='period').agg({'count':np.size, 'mean':np.mean,'median':np.median,'min':np.min,'max':np.max,'std':np.std})
    tsom.loc[tsom['count']<mindayspermonth*numperday,['mean','median','min','max','std']] = 'NaN'
    #add columns for custom date format
    tsom['yy']=tsom.index.year
    tsom['mm']=tsom.index.month
    tsom['dd']=15
    tsom['mean']=tsom['mean'].astype(float)   # makes for cleaner format on output to csv
    tsom['std']=tsom['std'].astype(float)   # makes for cleaner format on output to csv
    output_fmt=['yy','mm','dd','count','mean','median','min','max','std']
    tsomp=tsom.reindex(columns=output_fmt)# found I needed to generate a new dataframe to print in this order
    tsomp.to_csv(outdir+site[k]+'_wtmp_ma_'+str(depth)+'.csv',index=False,header=False,na_rep='NaN',float_format='%10.2f')

    #create a Annual mean
    tsoy=tso.resample('A',kind='period').agg({'count':np.size, 'mean':np.nanmean,'median':np.median,'min':np.min,'max':np.max,'std':np.std})
    if site[k]=='NARR': # special case for this site since sample frequency changed
      tsoy.loc[(tsoy['count']<350)&(tsoy.index.year<2001),['mean','median','min','max','std']] = 'NaN'
      tsoy.loc[(tsoy['count']<8000)&(tsoy.index.year>=2001),['mean','median','min','max','std']] = 'NaN'
    elif site[k]=='WHAQ': # special case for this site since sample frequency changed
      tsoy.loc[(tsoy['count']<12)&(tsoy.index.year<1962),['mean','median','min','max','std']] = 'NaN'  #monthly samples
      tsoy.loc[(tsoy['count']<350)&(tsoy.index.year>=1962),['mean','median','min','max','std']] = 'NaN'#daily
      tsoy.loc[(tsoy['count']<8000)&(tsoy.index.year>=2001),['mean','median','min','max','std']] = 'NaN'#hourly
    else:
      minsamperyear=0.8*np.max(tsoy['count'])# 80% of the maximum #per year
      tsoy.loc[tsoy['count']<minsamperyear,['mean','median','min','max','std']] = 'NaN' # if # months are not covered, set that year to NaN
    #add columns for custom date format
    tsoy['yy']=tsoy.index.year
    tsoy['mm']=12
    tsoy['dd']=31
    tsoy['mean']=tsoy['mean'].astype(float)   # makes for cleaner format on output to csv
    tsoy['std']=tsoy['std'].astype(float)   # makes for cleaner format on output to csv
    output_fmt=['yy','mm','dd','count','mean','median','min','max','std']
    tsoyp=tsoy.reindex(columns=output_fmt)# found I needed to generate a new dataframe to print in this order
    tsoyp.to_csv(outdir+site[k]+'_wtmp_ya_'+str(depth)+'.csv',index=False,header=False,na_rep='NaN',float_format='%10.2f')
 
    #create daily climatolgies using daily means
    newindex=[]
    for j in range(len(tsod)):    
        newindex.append(tsod['mean'].index[j].replace(year=2000,tzinfo=None)) # puts all observations in the same year, 2000
        # Note: I added this tzinfo=None in Aug 2014 because of a bug in Pandas 
    tsodnew=Series(tsod['mean'].values,index=newindex).sort_index()
    # trouble with this section in March 2016 since there is was apparently some "non numeric" values so I added the previous line
    tsdc=tsodnew.resample('D').agg({'count':np.size, 'mean':np.mean,'median':np.median,'min':np.min,'max':np.max,'std':np.std})    #add columns for custom date format
    tsdc['yy']=0
    tsdc['mm']=tsdc.index.month
    tsdc['dd']=tsdc.index.day
    tsdc['mean']=tsdc['mean'].astype(float)   # makes for cleaner format on output to csv
    tsdc['std']=tsdc['std'].astype(float)   # makes for cleaner format on output to cs    
    output_fmt=['yy','mm','dd','count','mean','median','min','max','std']
    tsdcp=tsdc.reindex(columns=output_fmt)# found I needed to generate a new dataframe to print in this order
    tsdcp.to_csv(outdir+site[k]+'_wtmp_dc_'+str(depth)+'.csv',index=False,header=False,na_rep='NaN',float_format='%10.2f')

    #create monthly climatologies using monthly means
    newindex=[]
    for j in range(len(tsom)):    
        newindex.append(tsom['mean'].index[j].to_timestamp().replace(year=2000,tzinfo=None)) # puts all observations in the same year, 2000
        # Note: I added this tzinfo=None in Aug 2014 because of a bug in Pandas 
    tsomnew=Series(tsom['mean'].values,index=newindex).sort_index()
    # trouble with this section in March 2016 since there is was apparently some "non numeric" values so I added the previous line
    tsmc=tsomnew.resample('M').agg({'count':np.size, 'mean':np.mean,'median':np.median,'min':np.min,'max':np.max,'std':np.std})    #add columns for custom date format
    tsmc['yy']=0
    tsmc['mm']=tsmc.index.month
    tsmc['dd']=tsmc.index.day
    tsmc['mean']=tsmc['mean'].astype(float)   # makes for cleaner format on output to csv
    tsmc['std']=tsmc['std'].astype(float)   # makes for cleaner format on output to cs    
    output_fmt=['yy','mm','dd','count','mean','median','min','max','std']
    tsmcp=tsmc.reindex(columns=output_fmt)# found I needed to generate a new dataframe to print in this order
    tsmcp.to_csv(outdir+site[k]+'_wtmp_mc_'+str(depth)+'.csv',index=False,header=False,na_rep='NaN',float_format='%10.2f')

    '''
    tsmccount=tsdc['count'].resample('m').agg({'count':np.size, 'mean':np.mean,'median':np.median,'min':np.min,'max':np.max,'std':np.std})
    tsmcmean=tsdc['mean'].resample('m').agg({'count':np.size, 'mean':np.mean,'median':np.median,'min':np.min,'max':np.max,'std':np.std})
    tsmcmedian=tsdc['median'].resample('m').agg({'count':np.size, 'mean':np.mean,'median':np.median,'min':np.min,'max':np.max,'std':np.std})
    tsmcmin=tsdc['min'].resample('m').agg({'count':np.size, 'mean':np.mean,'median':np.median,'min':np.min,'max':np.max,'std':np.std})
    tsmcmax=tsdc['max'].resample('m').agg({'count':np.size, 'mean':np.mean,'median':np.median,'min':np.min,'max':np.max,'std':np.std})
    tsmcstd=tsdc['std'].resample('m').agg({'count':np.size, 'mean':np.mean,'median':np.median,'min':np.min,'max':np.max,'std':np.std})
    
    tsmc['count']=0
    tsmc['min']=0.
    tsmc['max']=0.
    tsmc['std']=0.
    ##########get each month's count,min,max,std mean value###############
    tcount=tsdc['count'].resample('m')
    tmi=tsdc['min'].resample('m')
    tma=tsdc['max'].resample('m')
    tstd=tsdc['std'].resample('m')
    for kk in range(len(tsmc)):
       tsmc['count'].values[kk]=tcount[kk]
       tsmc['min'].values[kk]=tmi[kk]
       tsmc['max'].values[kk]=tma[kk]
       tsmc['std'].values[kk]=tstd[kk]
    tsmc['yy']=0
    tsmc['mm']=tsmc.index.month
    tsmc['dd']=0
    output_fmt=['yy','mm','dd','count','mean','median','min','max','std']
    
    tsmcpcount=tsmccount.reindex(columns=output_fmt)# found I needed to generate a new dataframe to print in this order
    tsmcpcount.to_csv(outdir+site[k]+'_wtmp_mc_'+str(int(depth))+'.csv',index=False,header=False,na_rep='NaN',float_format='%10.2f')
    '''
    output_fmt_html=['mm','count','mean','median','min','max','std']
    outhtml=tsmcp.to_html(header=True,index=False,na_rep='NaN',float_format=lambda x: '%10.2f' % x,columns=output_fmt_html)
    
    #make three plots: 1- daily means, 2- annual, and 3- seasonal cycle

    plt.figure() # daily mean
    tsod['mean'].astype(float).plot() #plot daily mean after getting rid of non-nmeric values
    plt.title(site[k]+' daily means')
    plt.show()
    plt.savefig(pltdir+site[k]+'_jt.png')
    
    plt.figure() # annual mean
    tsoy['mean'].dropna().astype(float).plot(marker='.',linewidth=2,markersize=20) #plot annual mean after getting rid of non-nmeric values
    plt.title(site[k]+' annual means')
    #thismanager = plt.get_current_fig_manager()
    #thismanager.window.setGeometry(50,100,640, 545)
    plt.show()
    plt.savefig(pltdir+site[k]+'_annual_clim.png')
    
    plt.figure() # seasonal cycle
    tt=tsmc['mean'].astype(float).plot() #plot mthly clim
    tt.xaxis.set_major_formatter(DateFormatter('%b'))
    plt.title(site[k]+' Monthly Climatology')
    plt.show()
    plt.savefig(pltdir+site[k]+'_seacycle.png')
    plt.close('all')
  
