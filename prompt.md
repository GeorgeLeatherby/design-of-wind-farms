Overall goal: Instead of using a .nc file create a windrose from a provided Weibull distribution. Do this only for the denmark site! The workflow via an .nc path needs to stay persistent for all other sites. 

Detailed description: To decide wether to use a .nc path or not, always check the value inside nc_file_path which is inside wind which is a key in the config json. If nc_file_path is null, go and check if there is a .csv file path to the parameters of the weibull distribution. You can check this in the variable weibull_distribution_path. Load the information inside the .csv. It contains the header names: wd,scale,shape,rel. frequency. 

We use diferent discretizations throughout the code. This needs to be taken into account when calling upscale function!

Reference code for how to procede with the saved data points in the .csv file is below. Note that we operate with a single ti parameter not a table.

# Discretize Weibull for WindRose floris object
# a) Format and reshape
wb_scale = np.reshape(np.array(A),(-1,1))
wb_shape = np.reshape(np.array(k),(-1,1))
wb_wd_freq = np.reshape(np.array(freq),(-1,1))
# b) Wind speed discretization
wb_ws = np.arange(0, 51, ws_step)     # make sure full frequency spectrum is covered
# c) Upper and lower boundaries of wind speed bins
ws_low = np.arange(np.min(wb_ws)-ws_step/2,np.max(wb_ws)+ws_step/2,ws_step)
ws_high = ws_low + ws_step
ws_low[ws_low<0] = 0
ws_high[ws_high<0] = 0
# d) Discretize distribution for each wind direction and store in list (Weibull CDF)
freq_grid_raw = wb_wd_freq * ((1 - np.exp(-(1 / wb_scale * ws_high) ** wb_shape)) -
              (1 - np.exp(-(1 / wb_scale * ws_low) ** wb_shape)))

# create windrose object
wind_rose = WindRose(
    wind_directions=np.array(wd_wb),
    wind_speeds=wb_ws,
    ti_table=TI_grid,
    freq_table=freq_grid_raw,
)
wind_rose = wind_rose.upsample(wd_step=wd_step, ws_step=ws_step)