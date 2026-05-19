# imports
from netCDF4 import Dataset, num2date
import numpy as np
import pandas as pd
from floris import FlorisModel, TimeSeries
import matplotlib.pyplot as plt
from external.landbosse.landbosse.main_function import run_landbosse
import time
from scipy.optimize import minimize

class Assignment5:
    """
    This assignment aims at introducing students to optimization problems in general and to cost
    based layout optimization specifically, including understanding an open-source gradient-free 
    optimization algorithm, setting up the objective function dependent on the design variables, 
    defining constraints and boundaries, investigating convergence, and analysing the results 
    delivered by the optimization algorithm in the context of wind farm layout optimization. 
    Furthermore, students learn how to set up FLORIS based on wind resource time series retrieved 
    from a wind atlas. 

    Eight IEA 3.4MW wind turbines are planned to be installed around Munich within a square 
    boundary (2.8 x 2.8 km) and with a minimum separation distance of 2D between all turbines. The 
    substation is placed in the center point of the boundary. 
    """

    def __init__(self):
        """class constructor"""

        # Init given data
        self.D = 130 # m (turbine diameter)
        self.turbine_type = "IEA3_4_MW" # Turbine type

        if self.turbine_type == "IEA3_4_MW":
            self.reference_wind_height = 120 # m
        else:
            self.reference_wind_height = None

        self.wake_model_path = r"inputs/gch.yaml" # Path to the yaml file for the wake model

        self.rated_power_single_turbine = 3370 # kW
        self.num_turbines = 8

        self.nominal_discount_rate = 0.04 # %
        self.turbine_costs = 1.3 * 1e6 # $/MW
        self.o_m_costs = 0.016 # $/kWh
        self.rental_costs = 20000 # $/MW-year
        self.fuel_costs = 5.19 # $/gallon
        self.electricity_price = 67 # $/MWh
        self.line_frequency = 50 # Hz
        self.array_voltage = 30 # kV
        self.project_construction_time = 12 # months
        self.project_lifetime = 20 # years

        self.wind_shear = 0.2 # Wind shear exponent
        self.ti = 0.06 # Turbulence intensity

        # (x, y) coordinates of the initial layout in km
        self.initial_layout = np.array(
            [[0.8, 1.2], [1.2, 1.2], [1.6, 1.2], [2.0, 1.2], 
             [0.8, 1.6], [1.2, 1.6], [1.6, 1.6], [2.0, 1.6]]) 
        
        # (x, y) coordinates of the substation in km. Center point of the boundary.
        self.fixed_substation_location = np.array([[1.4, 1.4]])

        # Define the boundary of the wind farm in km
        self.boundary = [(0, 0), (2.8, 0), (2.8, 2.8), (0, 2.8)]

        self.min_separation_distance = 2 * self.D # Minimum separation distance between turbines in m, where D is the rotor diameter

        # Run the assignment
        self.run()
        
    def run(self):
        print("\nTask 1: Load dataset then calculate and plot wind profile:")
        # task 1: load the dataset, calculate the vertical wind profile at 120m, calculate the wind rose object and plot the wind rose
        df = self.load_dataset()
        df = self.vertical_wind_profile_power_law(df, z=120, zr=10, wind_shear=self.wind_shear)
        wind_rose = self.calculate_windrose_object(df, discret_wind_dir=5, discret_wind_speed=1, ti=self.ti)
        self.plot_wind_rose(wind_rose, reference_height=120)

        # task 2: AEP, Capacity factor, farm efficiency, LCOE, and profitability index for the initial layout using gaussian wake model
        print("\nTask 2: Initial layout performance metrics:")
        self.fmodel = self.init_set_run_floris_model(self.initial_layout, wind_rose, self.turbine_type, self.reference_wind_height, self.wake_model_path, nowake = False)
        self.fmodel_no_wake = self.init_set_run_floris_model(self.initial_layout, wind_rose, self.turbine_type, self.reference_wind_height, self.wake_model_path, nowake = True)

        aep = self.calculate_aep(self.fmodel)
        aep_no_wake = self.calculate_aep(self.fmodel_no_wake)
        capacity_factor = self.calculate_capacity_factor(aep, self.rated_power_single_turbine, self.num_turbines)
        farm_efficiency = self.calculate_farm_efficiency(aep, aep_no_wake)

        print(f"AEP: {aep:.2f} Wh")
        print(f"Capacity Factor: {capacity_factor:.4f}")
        print(f"Farm Efficiency: {farm_efficiency:.2f} %")

        # use landbosse to calculate costs
        landbosse_results_df = run_landbosse(
            Turbine_coordinates=self.initial_layout,
            Substation_coordinate=self.fixed_substation_location,
            Desired_Voltage=self.array_voltage,
            WriteExcel=False,
            Display=False
        )

        # print(landbosse_results_df)
        
        lcoe = self.calculate_lcoe(aep, landbosse_results_df)
        pi = self.calculate_pi(aep, landbosse_results_df)

        print(f"LCOE: {lcoe:.2f} $/MWh")
        print(f"Profitability Index: {pi:.4f}")

        # task 3: optimization of the layout using scipy minimize and the same performance metrics as in task 2 for the optimized layout
        print("\nTask 3: Optimize layout and calculate performance metrics for optimized layout:")
        optimizer = LayoutOptimizer()

        self.show_plots()

    def load_dataset(self):
        # Load the CDF4 dataset and extract the required variables
        filepath = "mesotimeseries-Point 1.nc"
        cdf_dataset = Dataset(filepath, mode='r')
        print(cdf_dataset.variables.keys())

        time_var = cdf_dataset.variables['time']
        times = num2date(time_var[:], time_var.units, calendar=getattr(time_var, 'calendar', 'standard'))
        timestamps = pd.to_datetime([str(t) for t in times])
        print(timestamps)

        wind_speed = np.squeeze(cdf_dataset.variables['WS10'][:])
        print(wind_speed)

        wind_direction = np.squeeze(cdf_dataset.variables['WD10'][:])
        print(wind_direction)

        # 4. Grab the latitude and longitude values for reference (optional)
        # Taking the first element [0, 0] assuming it's a single point grid
        lat = cdf_dataset.variables['XLAT'][0, 0] if cdf_dataset.variables['XLAT'].ndim == 2 else cdf_dataset.variables['XLAT'][0]
        lon = cdf_dataset.variables['XLON'][0, 0] if cdf_dataset.variables['XLON'].ndim == 2 else cdf_dataset.variables['XLON'][0]

        # 5. Build the Pandas DataFrame
        df = pd.DataFrame({
            'timestamp': timestamps,
            'ws_10m': wind_speed,
            'wd_10m': wind_direction
        })

        # Set timestamp as the index for time-series operations
        df.set_index('timestamp', inplace=True)

        # 6. Safely close the file
        cdf_dataset.close()

        # Print location details and the top of the dataframe
        print(f"Extracted data for Coordinates: Lat {lat:.4f}, Lon {lon:.4f}")
        print(df.head())

        return df


    def vertical_wind_profile_power_law(self, df, z, zr, wind_shear):
        """
        Calculate the vertical wind profile using the power law. Transforms an entire dataframe column of wind speeds at a reference height to a new height.
        Uses the formula: U(z) = U(zr) * (z / zr) ** windshear. Only works if the dataframe has a column named 'ws_10m' for the reference wind speeds.

        Returns:
        dataframe: A new dataframe with:
        - calculated wind speeds at height z,
        - the same timestamps as the input dataframe
        - the same wd_10m values as the input dataframe (since wind direction is not affected by height in this model)   

        Parameters:
        z (float): Height at which to calculate the wind speed (m)
        zr (float): Reference height (m)
        windshear (float): Wind shear exponent
        """

        # Ensure that the dataframe has the required column
        if 'ws_10m' not in df.columns:
            raise ValueError("DataFrame must contain 'ws_10m' column for reference wind speeds.")

        # Calculate the wind speed at height z using the power law
        df[f'ws_{z}m'] = df['ws_10m'] * (z / zr) ** wind_shear

        # Return dataframe with the new wind speed column 
        return df


    def calculate_windrose_object(self, df, discret_wind_dir, discret_wind_speed, ti):
        """
        Calculate the wind rose object based on discretized wind direction and speed data.
        Requires the wanted dataframe to be given
        """
        # Transfer df into floris TimeSeries
        timeseries = TimeSeries(wind_speeds=df['ws_120m'].values, wind_directions=df['wd_10m'].values, turbulence_intensities=ti)
        # Create the wind rose object using the discretized wind direction and speed data
        wind_rose = timeseries.to_WindRose(
            wd_edges= np.arange(0, 360, discret_wind_dir),
            ws_edges= np.arange(0, 50, discret_wind_speed)
        )

        return wind_rose


    def plot_wind_rose(self, wind_rose, reference_height):
        """
        Plot the wind rose using the calculated wind rose object.
        """
        # Plot the wind rose
        wind_rose.plot()
        plt.title(f"Wind Rose at {reference_height}m")


    def show_plots(self):
        plt.tight_layout()
        plt.show()


    def init_set_run_floris_model(self, layout, wind_rose, turbine_type, reference_wind_height, wake_model_path, nowake):
        """
        Initialize, set up, and run the FLORIS model based on the given layout, wind rose, turbine type, reference wind height, and wake model path.
        """
        # Initialize the FLORIS model with the given parameters
        fmodel = FlorisModel(wake_model_path)

        # Set up the FLORIS model with the given layout, wind rose, turbine type, and reference wind height
        fmodel.set(
            layout_x = layout[:, 0] * 1000, # Convert km to m
            layout_y = layout[:, 1] * 1000, # Convert km to m
            wind_data = wind_rose,
            turbine_type = [turbine_type],
            reference_wind_height = reference_wind_height,
            wind_shear=self.wind_shear
        )

        if nowake:
            # Run the FLORIS model without wake effects
            fmodel.run_no_wake()
        else:
            # Run the FLORIS model
            fmodel.run()

        return fmodel
    
    def calculate_aep(self, fmodel):
        """
        Calculate the Annual Energy Production (AEP) based on the FLORIS model results.
        Returns AEP in Wh!
        """
        aep = fmodel.get_farm_AEP()
        return aep
    
    def calculate_capacity_factor(self, aep, rated_power_single_turbine, num_turbines):
        """
        Calculate the capacity factor based on the AEP, rated power, and number of turbines.
        Assumes rated power in kw.
        Assumes AEP in Wh.
        """
        # Calculate the total rated power of the farm in kW
        total_rated_power_kw = rated_power_single_turbine * num_turbines

        # Calculate the maximum possible energy production in a year in Wh
        max_energy_production_wh = total_rated_power_kw * 1000 * 24 * 365

        # Calculate the capacity factor
        capacity_factor = aep / max_energy_production_wh

        return capacity_factor
    
    def calculate_farm_efficiency(self, aep_wake, aep_no_wake):
        """
        Calculate the farm efficiency based on the FLORIS model results with and without wake effects.
        Returns farm efficiency as a percentage.
        """
        # Calculate the farm efficiency
        farm_efficiency = (aep_wake / aep_no_wake) * 100

        return float(farm_efficiency)
    

    def calculate_lcoe(self, aep, landbosse_results_df):
        """
        Calculate Levelized Cost of Energy (LCOE) in $/MWh
        
        Inputs:
        aep (float): Annual Energy Production in Wh.
        landbosse_results_df (DataFrame): LandBOSSE cost output.
        """
        # Convert AEP to MWh and kWh to align with cost unit variables
        aep_mwh = aep / 1e6
        aep_kwh = aep / 1000
        
        # Initial Investment (I)
        total_capacity_mw = (self.rated_power_single_turbine / 1000) * self.num_turbines
        turbine_cost_total = self.turbine_costs * total_capacity_mw
        bos_cost_total = landbosse_results_df['Cost per project'].sum()
        I = turbine_cost_total + bos_cost_total
        
        # Annual O&M costs
        # Combines the per-kWh O&M costs and the annual per-MW rental costs
        annual_om_cost = (self.o_m_costs * aep_kwh) + (self.rental_costs * total_capacity_mw)
        
        # Annuity factor (A)
        d = self.nominal_discount_rate
        N = self.project_lifetime
        A = ((1 + d)**N - 1) / (d * (1 + d)**N)
        
        # LCOE ($/MWh)
        lcoe = (I / (aep_mwh * A)) + (annual_om_cost / aep_mwh)
        
        return lcoe
    
    def calculate_pi(self, aep, landbosse_results_df):
        """
        Calculate Profitability Index (PI) based on lecture formulas.
        
        Inputs:
        aep (float): Annual Energy Production in Wh.
        landbosse_results_df (DataFrame): LandBOSSE cost output.
        """
        aep_mwh = aep / 1e6
        aep_kwh = aep / 1000
        
        # Initial Investment (I)
        total_capacity_mw = (self.rated_power_single_turbine / 1000) * self.num_turbines
        turbine_cost_total = self.turbine_costs * total_capacity_mw
        bos_cost_total = landbosse_results_df['Cost per project'].sum()
        I = turbine_cost_total + bos_cost_total
        
        # Annual Net Cash Flow (F_n)
        annual_revenue = aep_mwh * self.electricity_price
        annual_om_cost = (self.o_m_costs * aep_kwh) + (self.rental_costs * total_capacity_mw)
        F_n = annual_revenue - annual_om_cost
        
        # Annuity factor (A)
        d = self.nominal_discount_rate
        N = self.project_lifetime
        A = ((1 + d)**N - 1) / (d * (1 + d)**N)
        
        # Present Value of future cash flows and PI
        pv_future_cashflows = F_n * A
        pi = pv_future_cashflows / I
        
        return pi
    

class LayoutOptimizer(Assignment5):
    """
    Subclass of Assignment5 that overrides the run method to perform 
    wind farm layout optimization using the COBYLA algorithm. 
    The objective is to minimize LCoE while respecting boundaries 
    and minimum distance constraints.
    """
    def __init__(self):
        # We call the super constructor. Note: because super().__init__() 
        # normally calls self.run(), overriding run() here ensures that 
        # only our optimization workflow gets executed on instantiation.
        super().__init__()

    def run(self):
        """
        Overriden run method to focus specifically on the layout optimization 
        deliverables. Calculates the base wind rose once, defines the layouts, 
        and runs the optimization routine.
        """
        print("\nLoading dataset and preparing wind profile...")
        df = self.load_dataset()
        df = self.vertical_wind_profile_power_law(df, z=120, zr=10, wind_shear=self.wind_shear)
        
        # Save wind_rose as class attribute to prevent recalculating it in the objective function
        self.wind_rose = self.calculate_windrose_object(df, discret_wind_dir=5, discret_wind_speed=1, ti=self.ti)
        
        # Set normalized system bounds (2.8 km border = 1.0 in normalized space)
        self.norm_scale = 2.8 
        self.min_dist_norm = (self.min_separation_distance / 1000) / self.norm_scale 

        # Design Choice 1: Normalized Initial Layout 1
        # 4 corners, 4 mid-boundary edges. 
        self.layout1_norm = np.array([
            [0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], # Corners
            [0.5, 0.0], [1.0, 0.5], [0.5, 1.0], [0.0, 0.5]  # Half boundaries
        ])

        # Design Choice 2: Normalized Initial Layout 2
        # Middle y=0 and y=1 boundaries moved inwards by 0.25y
        self.layout2_norm = np.array([
            [0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], 
            [0.5, 0.25], [1.0, 0.5], [0.5, 0.75], [0.0, 0.5] 
        ])

        # Optimize Layout 1
        print("\n--- Starting Optimization for Layout 1 ---")
        final_layout1, time1 = self.optimize_layout(self.layout1_norm)
        self.plot_results(self.layout1_norm, final_layout1, time1, "Layout 1")

        # Optimize Layout 2
        print("\n--- Starting Optimization for Layout 2 ---")
        final_layout2, time2 = self.optimize_layout(self.layout2_norm)
        self.plot_results(self.layout2_norm, final_layout2, time2, "Layout 2")


    def objective(self, layout_flat):
        """
        Objective function calculating LCoE.
        Shape expectation: layout_flat is a 1D array of length 16.
        It is reshaped to (8, 2) and scaled back up to km for FLORIS & LandBOSSE.
        """
        # 1. Reshape and denormalize back to km space
        layout_norm = layout_flat.reshape(-1, 2)
        layout_km = layout_norm * self.norm_scale
        
        # 2. Evaluate performance via FLORIS 
        fmodel = self.init_set_run_floris_model(
            layout=layout_km, 
            wind_rose=self.wind_rose, 
            turbine_type=self.turbine_type, 
            reference_wind_height=self.reference_wind_height, 
            wake_model_path=self.wake_model_path, 
            nowake=False
        )
        aep = self.calculate_aep(fmodel)
        
        # 3. Evaluate costs via LandBOSSE
        landbosse_df = run_landbosse(
            Turbine_coordinates=layout_km,
            Substation_coordinate=self.fixed_substation_location,
            Desired_Voltage=self.array_voltage,
            WriteExcel=False, 
            Display=False
        )
        
        # 4. Calculate LCoE
        lcoe = self.calculate_lcoe(aep, landbosse_df)
        
        # Keep track of history to plot the convergence curve later
        self.lcoe_history.append(lcoe)
        
        return lcoe


    def optimize_layout(self, initial_layout_norm):
        """
        Wrapper to configure bounds, constraints, and execute COBYLA.
        Returns the optimized final layout in normalized coordinates and execution time.
        """
        self.lcoe_history = [] 
        
        constraints = []
        num_vars = self.num_turbines * 2

        # 1. Boundary Constraints (0 <= x <= 1 and 0 <= y <= 1)
        # COBYLA requires constraints in the form of C(x) >= 0.
        def lower_bound(var, idx): return var[idx]
        def upper_bound(var, idx): return 1.0 - var[idx]

        for i in range(num_vars):
            constraints.append({'type': 'ineq', 'fun': lower_bound, 'args': (i,)})
            constraints.append({'type': 'ineq', 'fun': upper_bound, 'args': (i,)})

        # 2. Minimum Distance Constraint
        # Calculate euclidian distance between pair points -> must be > min_dist_norm
        def distance_constraint(var, i, j):
            xi, yi = var[2 * i], var[2 * i + 1]
            xj, yj = var[2 * j], var[2 * j + 1]
            return np.sqrt((xi - xj)**2 + (yi - yj)**2) - self.min_dist_norm

        for i in range(self.num_turbines):
            for j in range(i + 1, self.num_turbines):
                constraints.append({'type': 'ineq', 'fun': distance_constraint, 'args': (i, j)})

        # Flatten initial guess array for scipy compatibility 
        x0 = initial_layout_norm.flatten()
        
        start_time = time.time()
        # Execute COBYLA optimization
        res = minimize(
            fun=self.objective,
            x0=x0,
            method='COBYLA',
            constraints=constraints,
            options={'rhobeg': 0.35, 'maxiter': 300, 'disp': 0}
        )
        comp_time = time.time() - start_time
        
        print(f"Optimization finished in {comp_time:.2f} seconds.")
        print(f"Success: {res.success}. Message: {res.message}")
        
        return res.x.reshape(-1, 2), comp_time


    def plot_results(self, initial_layout_norm, final_layout_norm, comp_time, layout_name):
        """
        Creates a figure showing layout improvements, the convergence curve 
        of LCoE calculations across iterations, and requested resulting metrics.
        """
        # De-normalize coordinates for mapping and metric calculation
        init_km = initial_layout_norm * self.norm_scale
        final_km = final_layout_norm * self.norm_scale
        
        # Run final models to retrieve evaluation metrics for final output
        fmodel = self.init_set_run_floris_model(final_km, self.wind_rose, self.turbine_type, self.reference_wind_height, self.wake_model_path, nowake=False)
        fmodel_nw = self.init_set_run_floris_model(final_km, self.wind_rose, self.turbine_type, self.reference_wind_height, self.wake_model_path, nowake=True)
        
        aep = self.calculate_aep(fmodel)
        aep_nw = self.calculate_aep(fmodel_nw)
        cf = self.calculate_capacity_factor(aep, self.rated_power_single_turbine, self.num_turbines)
        eff = self.calculate_farm_efficiency(aep, aep_nw)
        
        landbosse_df = run_landbosse(final_km, self.fixed_substation_location, self.array_voltage, False, False)
        lcoe = self.calculate_lcoe(aep, landbosse_df)
        pi = self.calculate_pi(aep, landbosse_df)
        
        # Create Plots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 12))
        
        # Subplot 1: Map Layout
        boundary_line_x = [0, self.norm_scale, self.norm_scale, 0, 0]
        boundary_line_y = [0, 0, self.norm_scale, self.norm_scale, 0]
        
        ax1.plot(boundary_line_x, boundary_line_y, label='Boundaries', color='blue')
        ax1.scatter(self.fixed_substation_location[0,0], self.fixed_substation_location[0,1], marker='s', color='orange', s=100, label='Substation')
        ax1.scatter(init_km[:,0], init_km[:,1], color='gray', label='Initial Turbine Positions', alpha=0.5, s=60)
        ax1.scatter(final_km[:,0], final_km[:,1], color='green', label='Final Turbine Positions', s=60)
        
        ax1.set_xlim(-0.2, 3.0)
        ax1.set_ylim(-0.2, 3.0)
        ax1.set_aspect('equal')
        ax1.set_xlabel("x-pos [km]")
        ax1.set_ylabel("y-pos [km]")
        ax1.set_title(f"Optimized Topology: {layout_name}")
        ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax1.grid(True)
        
        # Subplot 2: Convergence History
        ax2.plot(self.lcoe_history, label='LCoE', color='purple', linewidth=2)
        ax2.set_xlabel('Iteration Step')
        ax2.set_ylabel('LCoE [$/MWh]')
        ax2.set_title(f"LCoE Convergence Curve ({layout_name})")
        ax2.grid(True)
        
        # Inject Results Text Block below graph
        results_text = (
            f"--- Final Layout Optimization Metrics ---\n"
            f"Computation Time: {comp_time:.2f} s\n"
            f"Final AEP: {aep/1e9:.4f} GWh\n"
            f"Capacity Factor: {cf:.4f}\n"
            f"Farm Efficiency: {eff:.2f}%\n"
            f"Final LCoE: {lcoe:.3f} $/MWh\n"
            f"Profitability Index (PI): {pi:.4f}"
        )
        
        # Using transform map placing to pin it under the bounds of ax2 cleanly.
        ax2.text(0.5, -0.25, results_text, transform=ax2.transAxes, fontsize=11, 
                 ha='center', va='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.9))
                 

# Execution
assignment5 = Assignment5()