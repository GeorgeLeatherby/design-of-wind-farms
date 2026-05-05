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
from floris.flow_visualization import visualize_cut_plane
import floris.layout_visualization as layoutviz

class Assignment3:

    def __init__(self):
        self.farm_power_0_degrees_5D = None
        self.farm_power_0_degrees_10D = None

        # Execution
        self.task2()
        self.task3()
        self.task4()
        self.task5()
        self.task6()

        self.plot()

    def task2(self):
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
        # plt.show()


    def task3(self):
        """
        Task 3: Define the wind farm in FLORIS and visualize the wind farm flow field in the (a) horizontal 
        plane at hub height, (b) stream-wise plane, and (c) span-wise plane when the wind speed 
        is 7.5 m/s for two wind directions of 0° and 240° 
        """

        # We use the defined layout from the yaml file
        fmodel = FlorisModel("inputs/gch.yaml")

        # Set the wind speed and direction
        fmodel.set(
            wind_speeds=[7.5, 7.5],
            wind_directions=[0.0, 240.0],
            turbulence_intensities=[0.06, 0.06],
            turbine_type=["IEA3_4_MW", "IEA3_4_MW", "IEA3_4_MW"],
            wind_shear=0.14,
            layout_x=[0.0, 0.0, 0.0],
            layout_y=[0.0, 650.0, 1300.0]
        )
        
        fmodel.run()

        crossstream_dist = 650.0
        downstream_dist = 500.0

        for findex in [0, 1]:
            
            # Collect the data for 3 planes using pre-built methods
            horizontal_plane = fmodel.calculate_horizontal_plane(height=120.0, x_resolution=100, y_resolution=100, findex_for_viz=findex)
            y_plane = fmodel.calculate_y_plane(x_resolution=100, z_resolution=100, crossstream_dist=crossstream_dist, findex_for_viz=findex)
            cross_plane = fmodel.calculate_cross_plane(y_resolution=100, z_resolution=100, downstream_dist=downstream_dist, findex_for_viz=findex)

            # Plot the planes using pre-built methods
            fig1, ax1 = plt.subplots( figsize=(6, 5) )
            fig2, ax2 = plt.subplots( figsize=(6, 5) )
            fig3, ax3 = plt.subplots( figsize=(6, 5) )

            ax1 = visualize_cut_plane(horizontal_plane, ax=ax1, title=f"Horizontal Plane at 120 m", color_bar=True)
            ax2 = visualize_cut_plane(y_plane, ax=ax2, title=f"Y Plane at {crossstream_dist} m", color_bar=True)
            ax3 = visualize_cut_plane(cross_plane, ax=ax3, title=f"Cross Plane at {downstream_dist} m downstream distance", color_bar=True)

            # Plot the turbine rotors
            # layoutviz.plot_turbine_rotors(fmodel, ax=ax1)
            # layoutviz.plot_turbine_rotors(fmodel, ax=ax2)
            # layoutviz.plot_turbine_rotors(fmodel, ax=ax3)

            plt.tight_layout()

            # Save all generated graphs for the two wind directions in images folder
            fig1.savefig(f"images/assignment3_horizontal_plane_findex_{findex}.png", dpi=600)
            fig2.savefig(f"images/assignment3_y_plane_findex_{findex}.png", dpi=600)
            fig3.savefig(f"images/assignment3_cross_plane_findex_{findex}.png", dpi=600)

        # plt.show()

    def task4(self):
        """
        Use Jensen’s wake model (kw = 0.075), and determine the output power of each wind 
        turbine as well as the output power of the farm when the wind speed is 7.5 m/s for two 
        wind directions of 0° and 240°.
        """

        fmodel = FlorisModel("inputs/jensen.yaml")

        # Set the wind speed and direction
        fmodel.set(
            wind_speeds=[7.5, 7.5],
            wind_directions=[0.0, 240.0],
            turbulence_intensities=[0.06, 0.06],
            turbine_type=["IEA3_4_MW", "IEA3_4_MW", "IEA3_4_MW"],
            wind_shear=0.14,
            layout_x=[0.0, 0.0, 0.0],
            layout_y=[0.0, 650.0, 1300.0]
        )

        fmodel.run_no_wake()
        turbine_powers_no_wake = fmodel.get_turbine_powers()
        farm_power_no_wake = fmodel.get_farm_power()

        print(f"\nNo wake case 0°:")
        print(f"Turbine Powers (KW): {turbine_powers_no_wake[0]/1e3}")
        print(f"Farm Power (KW): {farm_power_no_wake[0]/1e3}")

        fmodel.run()
        turbine_powers = fmodel.get_turbine_powers()
        farm_power = fmodel.get_farm_power()

        print(f"\nWind direction: 0°:")
        print(f"Turbine Powers (KW): {turbine_powers[0]/1e3}")
        print(f"Farm Power (KW): {farm_power[0]/1e3}")

        self.farm_power_0_degrees_5D = farm_power[0]

        print(f"\nWind direction: 240°:")
        print(f"Turbine Powers (KW): {turbine_powers[1]/1e3}")
        print(f"Farm Power (KW): {farm_power[1]/1e3}")

        assignment2_turbine_powers_0_degrees = np.array([812.42, 872.36, 1515.15]) # (KW)
        assignment2_farm_power_0_degrees = 3199.93 # (KW)

        print(f"\nComparison with hand calculated values from assignment 2 for 0°:")
        print(f"Hand calculated turbine outputs (KW): {assignment2_turbine_powers_0_degrees}")
        print(f"Simulated turbine outputs (KW): {turbine_powers[0]/1e3}")
        print(f"Difference in turbine outputs in %: {(assignment2_turbine_powers_0_degrees - turbine_powers[0]/1e3) / assignment2_turbine_powers_0_degrees * 100}")
        print(f"Hand-calculated Farm Power (KW): {assignment2_farm_power_0_degrees}")
        print(f"Simulated Farm Power (KW): {self.farm_power_0_degrees_5D/1e3}")
        print(f"Difference in Farm Power (KW): {assignment2_farm_power_0_degrees - self.farm_power_0_degrees_5D/1e3}")
        print(f"Difference farm power in %: {(assignment2_farm_power_0_degrees - self.farm_power_0_degrees_5D/1e3) / assignment2_farm_power_0_degrees * 100}")

    def task5(self):
        """
        Repeat question 4 only for a wind direction of 0° and if the separation distance increases 
        to 10D. Calculate the relative difference (percentage) of the output power of the farm with 
        respect to the case of 5D.
        """

        fmodel = FlorisModel("inputs/jensen.yaml")

        # Set the wind speed and direction
        fmodel.set(
            wind_speeds=[7.5],
            wind_directions=[0.0],
            turbulence_intensities=[0.06],
            turbine_type=["IEA3_4_MW", "IEA3_4_MW", "IEA3_4_MW"],
            wind_shear=0.14,
            layout_x=[0.0, 0.0, 0.0],
            layout_y=[0.0, 1300.0, 2600.0]
        )

        fmodel.run()
        turbine_powers = fmodel.get_turbine_powers()
        farm_power = fmodel.get_farm_power()

        print(f"\nWind direction: 0° with 10D separation:")
        print(f"Turbine Powers (KW): {turbine_powers[0]/1e3}")
        print(f"Farm Power (KW): {farm_power[0]/1e3}")

        self.farm_power_0_degrees_10D = farm_power[0]

        relative_difference_farm_power = (self.farm_power_0_degrees_10D - self.farm_power_0_degrees_5D) / self.farm_power_0_degrees_5D * 100

        print(f"\nRelative difference in farm power between 5D and 10D cases: {relative_difference_farm_power:.2f}%")

    def task6(self):
        """
        Use the Gaussian wake model and determine the output power of each wind turbine and 
        visualize the flow field for night and day conditions when the wind speed is 7.5 m/s, wind 
        direction is 0° and the separations distance is 5D. Explain your answer and compare the 
        results and recovery of the turbine wakes for day and night. How do the wind shear and turbulence 
        intensity paramteres affect power generation? 
        """

        # Given paramteres for day and night conditions
        day_ws = 0.06
        day_ti = 0.12

        night_ws = 0.22
        night_ti = 0.06

        day_fmodel = FlorisModel("inputs/gch.yaml")
        night_fmodel = FlorisModel("inputs/gch.yaml")

        # Set the wind speed and direction for day conditions
        day_fmodel.set(
            wind_speeds=[7.5],
            wind_directions=[0.0],
            turbulence_intensities=[day_ti],
            turbine_type=["IEA3_4_MW", "IEA3_4_MW", "IEA3_4_MW"],
            wind_shear=day_ws,
            layout_x=[0.0, 0.0, 0.0],
            layout_y=[0.0, 650.0, 1300.0]
        )

        # Set the wind speed and direction for night conditions
        night_fmodel.set(
            wind_speeds=[7.5],
            wind_directions=[0.0],
            turbulence_intensities=[night_ti],
            turbine_type=["IEA3_4_MW", "IEA3_4_MW", "IEA3_4_MW"],
            wind_shear=night_ws,
            layout_x=[0.0, 0.0, 0.0],
            layout_y=[0.0, 650.0, 1300.0]
        )

        # Run the simulations
        day_fmodel.run()
        night_fmodel.run()

        # Get the turbine powers and farm power for day and night conditions
        day_turbine_powers = day_fmodel.get_turbine_powers()
        night_turbine_powers = night_fmodel.get_turbine_powers()

        # Get farm power for day and night conditions
        day_farm_power = day_fmodel.get_farm_power()
        night_farm_power = night_fmodel.get_farm_power()

        # Define the crossstream and downstream distances
        crossstream_dist = 650.0
        downstream_dist = 500.0

        # Visualize the flow fields for day and night conditions
        day_horizontal_plane = day_fmodel.calculate_horizontal_plane(height=120.0, x_resolution=100, y_resolution=100, findex_for_viz=0)
        night_horizontal_plane = night_fmodel.calculate_horizontal_plane(height=120.0, x_resolution=100, y_resolution=100, findex_for_viz=0)

        day_y_plane = day_fmodel.calculate_y_plane(x_resolution=100, z_resolution=100, crossstream_dist=crossstream_dist, findex_for_viz=0)
        night_y_plane = night_fmodel.calculate_y_plane(x_resolution=100, z_resolution=100, crossstream_dist=crossstream_dist, findex_for_viz=0)

        day_cross_plane = day_fmodel.calculate_cross_plane(y_resolution=100, z_resolution=100, downstream_dist=downstream_dist, findex_for_viz=0)
        night_cross_plane = night_fmodel.calculate_cross_plane(y_resolution=100, z_resolution=100, downstream_dist=downstream_dist, findex_for_viz=0)

        # Plot the planes using pre-built methods. Show day and night conditions side by side for comparison
        fig1, ax1 = plt.subplots(1, 2, figsize=(8, 5), constrained_layout=True)
        fig2, ax2 = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
        fig3, ax3 = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)

        # force same color scale for day/night on each plane
        hmin = min(day_horizontal_plane.df["u"].min(), night_horizontal_plane.df["u"].min())
        hmax = max(day_horizontal_plane.df["u"].max(), night_horizontal_plane.df["u"].max())

        ymin = min(day_y_plane.df["u"].min(), night_y_plane.df["u"].min())
        ymax = max(day_y_plane.df["u"].max(), night_y_plane.df["u"].max())

        cmin = min(day_cross_plane.df["u"].min(), night_cross_plane.df["u"].min())
        cmax = max(day_cross_plane.df["u"].max(), night_cross_plane.df["u"].max())

        visualize_cut_plane(day_horizontal_plane, ax=ax1[0], title=f"Day - Horizontal Plane at 120 m", color_bar=False, min_speed=hmin, max_speed=hmax)
        visualize_cut_plane(night_horizontal_plane, ax=ax1[1], title=f"Night - Horizontal Plane at 120 m", color_bar=False, min_speed=hmin, max_speed=hmax)

        visualize_cut_plane(day_y_plane, ax=ax2[0], title=f"Day - Y Plane at {crossstream_dist} m", color_bar=False, min_speed=ymin, max_speed=ymax)
        visualize_cut_plane(night_y_plane, ax=ax2[1], title=f"Night - Y Plane at {crossstream_dist} m", color_bar=False, min_speed=ymin, max_speed=ymax)

        visualize_cut_plane(day_cross_plane, ax=ax3[0], title=f"Day - Cross Plane at {downstream_dist} m downstream distance", color_bar=False, min_speed=cmin, max_speed=cmax)
        visualize_cut_plane(night_cross_plane, ax=ax3[1], title=f"Night - Cross Plane at {downstream_dist} m downstream distance", color_bar=False, min_speed=cmin, max_speed=cmax)

        mappable1 = ax1[0].collections[0]
        fig1.colorbar(mappable1, ax=ax1, orientation="vertical", label="Wind speed (m/s)")
        mappable2 = ax2[0].collections[0]
        fig2.colorbar(mappable2, ax=ax2, orientation="vertical", label="Wind speed (m/s)")
        mappable3 = ax3[0].collections[0]
        fig3.colorbar(mappable3, ax=ax3, orientation="vertical", label="Wind speed (m/s)")  

        # Plot the turbine rotors for horizontal plane for day and night conditions
        layoutviz.plot_turbine_rotors(day_fmodel, ax=ax1[0])
        layoutviz.plot_turbine_rotors(night_fmodel, ax=ax1[1])

        # Save all generated graphs for day and night conditions in images folder
        fig1.savefig(f"images/assignment3_day_night_horizontal_plane.png", dpi=600)
        fig2.savefig(f"images/assignment3_day_night_y_plane.png", dpi=600)
        fig3.savefig(f"images/assignment3_day_night_cross_plane.png", dpi=600)

        # print the turbine powers and farm power for day and night conditions
        print(f"\nDay conditions:")
        print(f"Turbine powers (KW): {day_turbine_powers/1e3}")
        print(f"Farm power (KW): {day_farm_power/1e3}")

        print(f"\nNight conditions:")
        print(f"Turbine powers (KW): {night_turbine_powers/1e3}")
        print(f"Farm power (KW): {night_farm_power/1e3}")

    def plot(self):
        plt.show()

# Run the assignment
assignment3 = Assignment3()