clim.py generates a set of csv files as needed by NERACOOS climatology page.
They are daily, monthly, and annual bottom temperature averages (along with daily and monthly climatologies) derived from eMOLT data on NEFSC ERDDAP server.
The code also produces plots for each site.
The csv files get stored in the "output" subfolder and the plots in "plots".

In order to decide which sites are worth posting on the NERACOOS climatology site, we also run two routines "getemolt_mostdata.py" and "plt_mostdata.py".
The latter helps visualize how many sites have at least "x" years time series and which ones have data from the most recent year.
