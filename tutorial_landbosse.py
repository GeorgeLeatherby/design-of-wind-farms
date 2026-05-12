from floris import FlorisModel, TimeSeries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from external.landbosse.landbosse.main_function import run_landbosse

# Load TimeSeries from csv
df = pd.read_csv("inputs/sample_time_series.csv")
ws = np.array(df["ws_HH_m/s"])
wd = np.array(df["wd_HH_deg"])

# Inputs
ti = 0.06
d_wd = 5 # deg (discretization for wind direction)
d_ws = 1 # m/s (discretization for wind speed)
D = 130 # m (turbine diameter)
x = [0.0, 0.0, 0.0] # m (turbine location)
y = [0.0, 5*D, 10*D] # m (turbine location)

# Setup FlorisModel
fmodel = FlorisModel("inputs/gch.yaml")

# Create TimeSeries object
timeseries = TimeSeries(wind_speeds=ws, wind_directions=wd, turbulence_intensities=ti)

# Create a windrose object
wind_rose = timeseries.to_WindRose(
    wd_edges = np.arange(0, 360, d_wd),
    ws_edges= np.arange(0, 50, d_ws)
    )

# Plot the windrose
wind_rose.plot(ws_step = d_ws*2, wd_step=d_wd*2)
plt.show()

fmodel.set(layout_x=x, layout_y=y, wind_data=wind_rose)
# Run the model
fmodel.run()

# get farm aep
aep = fmodel.get_farm_AEP()
print(f"Farm AEP: {aep/1e9:.3f} (GWh)")

# Re run the model with no wake
fmodel.run_no_wake()
aep_no_wake = fmodel.get_farm_AEP()
print(f"Farm AEP with no wake: {aep_no_wake/1e9:.3f} (GWh)")

wake_loss = (aep_no_wake - aep) / aep_no_wake * 100
print(f"Wake loss: {wake_loss:.2f} %")



""" Landbosse example"""
# Inputs
Turbine_coordinates = np.array([[0.0, 0.0], [0.0, 5*D], [0.0, 10*D]]) # m (turbine location)
Substation_coordinate = np.array([[200, 400]]) # m (substation location)
Cable_Voltage = 30 # (kV) Available: 10,20,30,45,60 kV
WriteExcel = False # Write excel file with results
Display = True # Display the results

# Run
landbosse_results = run_landbosse(
    Turbine_coordinates=Turbine_coordinates,
    Substation_coordinate=Substation_coordinate,
    Desired_Voltage=Cable_Voltage,
    WriteExcel=WriteExcel,
    Display=Display
)

total_project_costs = np.sum(landbosse_results["Cost per project"])
print("Landbosse results:")
print(landbosse_results)
print(f"Total project costs: {total_project_costs}")