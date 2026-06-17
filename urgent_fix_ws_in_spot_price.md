High level issue description: The wind speed for the spot price calculation must not be the mean windspeed! The wind speed for the spot price calculation must be taken from the actual wind data bins and power generation 

What to do:
- calculate using floris the annual wind production per wind speed bin. Extract the table from fmodel.get_farm_power(). From the windrose object get a frequency table for the windspeed bins. Windrose.freq_table. Element-wise multiple both tables with each other. Also multiply final elements with hours in a year 8760h. Then you have the energy matrix.
- Then you can sum-up per wind speed bin. and calculate the spot price for each. That provides the final income per year. 
- Loop through all the years.


Next thing:
Try SLSQP solver! Maybe as an additional option for the found solutions?