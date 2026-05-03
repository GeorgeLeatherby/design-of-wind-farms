"""
Assignment 3: Working with the floris library

Nomenclature:
- Ct: Thrust coefficient
- Cp: Power coefficient
- Power: Power output of the turbine (kW)
- Yaw angle: The angle at which the turbine is oriented relative to the incoming wind direction (degrees)
"""

import matplotlib.pyplot as plt
import numpy as np

from floris import FlorisModel



ws_array = np.arange(0.1, 30, 0.2)
wd_array = 270.0 * np.ones_like(ws_array)
turbulence_intensities = 0.06 * np.ones_like(ws_array)
yaw_angles = np.linspace(-30, 30, 60)
wind_speed_to_test_yaw = 7.5


# Task 2: Ct, Cp, Power and power-vs.-yaw curves for IEA 3.4 MW turbine (self-defined .yaml)

# Grab the gch model
fmodel = FlorisModel("inputs/gch.yaml")

# Make one turbine simulation
fmodel.set(layout_x=[0], layout_y=[0])

# Apply wind directions and wind speeds
fmodel.set(
    wind_speeds=ws_array, 
    wind_directions=wd_array, 
    turbulence_intensities=turbulence_intensities,
    wind_shear=0.14
)

# Instead of getting the list directly define the turbine to be used from assignment 3
turbines = ["IEA3_4_MW"]

# Declare a set of figures for comparing cp and ct across models
fig_cp_ct, axarr_cp_ct = plt.subplots(2, 1, sharex=True, figsize=(10, 10))

# For each turbine model available plot the basic info
for t in turbines:
    # Set t as the turbine
    fmodel.set(turbine_type=[t])
    fmodel.reset_operation() # Remove any previously applied yaw angles

    # Since we are changing the turbine type, make a matching change to the reference wind height
    fmodel.assign_hub_height_to_ref_height()

    # Create a figure
    fig, axarr = plt.subplots(1, 2, figsize=(10, 5))

    # Try a few density
    for density in [1.15, 1.225]:
        fmodel.set(air_density=density)
        
        # Plot cp and ct curves
        axarr_cp_ct[0].plot(
            fmodel.core.farm.turbine_map[0].power_thrust_table["wind_speed"],
            fmodel.core.farm.turbine_map[0].power_thrust_table["power_coefficient"],
            label=f"{t}, rho={density:.3f}", linestyle="dashed"
        )
        axarr_cp_ct[0].grid(True)
        axarr_cp_ct[0].legend()
        axarr_cp_ct[0].set_ylabel("Cp (-)")
        axarr_cp_ct[0].set_xlabel("Wind Speed (m/s)")
        axarr_cp_ct[0].set_title("Cp and Ct curves for different air densities")

        axarr_cp_ct[1].plot(
            fmodel.core.farm.turbine_map[0].power_thrust_table["wind_speed"],
            fmodel.core.farm.turbine_map[0].power_thrust_table["thrust_coefficient"],
            label=f"{t}, rho={density:.3f}", linestyle="dashed"
        )
        axarr_cp_ct[1].grid(True)
        axarr_cp_ct[1].legend()
        axarr_cp_ct[1].set_ylabel("Ct (-)")
        axarr_cp_ct[1].set_xlabel("Wind Speed (m/s)")

        # POWER CURVE
        ax = axarr[0]
        fmodel.set(
            wind_speeds=ws_array,
            wind_directions=wd_array,
            turbulence_intensities=turbulence_intensities,
        )
        fmodel.reset_operation() # Remove any previously applied yaw angles
        fmodel.run()
        turbine_powers = fmodel.get_turbine_powers().flatten() / 1e3
        if density == 1.225:
            ax.plot(ws_array, turbine_powers, label="Air Density = %.3f" % density, lw=1, color="b")
        else:
            ax.plot(ws_array, turbine_powers, label="Air Density = %.3f" % density, lw=1, color="r")
        ax.grid(True)
        ax.legend()
        ax.set_xlabel("Wind Speed (m/s)")
        ax.set_ylabel("Power (kW)")

        # Power loss to yaw, try a range of yaw angles
        ax = axarr[1]

        fmodel.set(
            wind_speeds=[wind_speed_to_test_yaw],
            wind_directions=[270.0],
            turbulence_intensities=[0.06],
        )
        yaw_result = []
        for yaw in yaw_angles:
            fmodel.set(yaw_angles=np.array([[yaw]]))
            fmodel.run()
            turbine_powers = fmodel.get_turbine_powers().flatten() / 1e3
            yaw_result.append(turbine_powers[0])
        if density == 1.225:
            ax.plot(yaw_angles, yaw_result, label="Air Density = %.3f (ref)" % density, lw=1, color="b")
        else:
            ax.plot(yaw_angles, yaw_result, label="Air Density = %.3f" % density, lw=1, color="r")

        # ax.plot(yaw_angles,yaw_result,label='Air Density = %.3f' % density)
        ax.grid(True)
        ax.legend()
        ax.set_xlabel("Yaw Error (deg)")
        ax.set_ylabel("Power (kW)")
        ax.set_title(f"Wind Speed = {wind_speed_to_test_yaw:.1f} (m/s)")

    # Give a suptitle
    fig.suptitle(t)

plt.show()


def calculate_cp(power, wind_speed, air_density, rotor_diameter):
    """
    Calculate the power coefficient (Cp) of a turbine given its power output, wind speed, air density, and rotor diameter.

    Parameters:
    - power: Power output of the turbine (kW)
    - wind_speed: Wind speed at the turbine (m/s)
    - air_density: Air density (kg/m^3)
    - rotor_diameter: Diameter of the turbine rotor (m)

    Returns:
    - Cp: Power coefficient (dimensionless)
    """
    # Convert power from kW to W
    power_watts = power * 1e3

    # Calculate the swept area of the rotor
    swept_area = np.pi * (rotor_diameter / 2) ** 2

    # Calculate the power available in the wind
    power_available = 0.5 * air_density * swept_area * wind_speed ** 3

    # Calculate Cp
    Cp = power_watts / power_available

    return Cp