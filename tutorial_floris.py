""" calculate power of singl inflow and plot """

from floris import FlorisModel
import matplotlib.pyplot as plt
from floris.flow_visualization import visualize_cut_plane

# Inputs
x = [0.0, 500.0, 1000.0]  # Turbine x-coordinates (m)
y = [0.0, 0.0, 0.0]       # Turbine y-coordinates (m)
wd = [270.0, 270.0]              # Wind direction (degrees)
ws = [8.0, 10.0]                # Wind speed (m/s)
ti = [0.06, 0.06]         # Turbulence intensity (-)

# Create the FlorisModel
# load basic settings and overwrite
fmodel = FlorisModel('inputs/gch.yaml')

# Note that in the yaml file  a lot settings are pre-defined!
fmodel.set(layout_x=x, layout_y=y, wind_directions=wd, wind_speeds=ws, turbulence_intensities=ti)

# Run flow field simulation
fmodel.run()

turbine_powers = fmodel.get_turbine_powers()
farm_power = fmodel.get_farm_power()

print(f"\nTurbine Powers (MW): {turbine_powers/1e6}")
print(f"Farm Power (MW): {farm_power/1e6}")

# Plot flow field
fig1, ax1 = plt.subplots()
fig2, ax2 = plt.subplots()

# calculate plane
horizontal_plane1 = fmodel.calculate_horizontal_plane(height=90.0, x_resolution=200, y_resolution=100, findex_for_viz=0)
horizontal_plane2 = fmodel.calculate_horizontal_plane(height=90.0, x_resolution=200, y_resolution=100, findex_for_viz=1)
# plot
visualize_cut_plane(horizontal_plane1, ax=ax1, title="Horizontal Plane at 90 m", color_bar=True)
visualize_cut_plane(horizontal_plane2, ax=ax2, title="Horizontal Plane at 90 m", color_bar=True)
plt.show()