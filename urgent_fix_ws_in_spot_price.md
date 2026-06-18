High level issue description: The wind speed for the spot price calculation must not be the mean windspeed! Using the mean windspeed for spot price calculation is wrong and results in too high of a compensation. The wind speed for the spot price calculation must be taken from the actual wind data bins. To calculate per year the actual compensation payments we need to use: actual prices based on the wind speed bins, wind energy production inside each wind speed 

What to do:
Using floris calculate the annual wind production per wind speed bin. Extract the table containing the annual wind production from fmodel.get_farm_power(). From the windrose object get a frequency table for the windspeed bins. For that use .freq_table. The tables should have the same dimensions. Check this prior to the following steps. Then perform element-wise multiplication using both tables (annular energy production and frequency) with each other. Then multiply final elements in resulting table with hours in a year 8760h. Then you have the finished energy production matrix. Then you can sum-up per wind speed bin and calculate the spot price for each energy production and wind speed frequency. Using the correctly calculated prices for each year it is possible to calculate the final income per year. 



Next thing:
Try SLSQP solver! Maybe as an additional option for the found solutions?