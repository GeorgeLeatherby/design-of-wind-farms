"""
final_assignment.py

Optimization of Wind Farm Layout for the Bavaria Site (Schlegelmuehle).
Maximizes Profitability Index (PI) across variable turbine counts (45-60 MW).
Includes NetCDF wind data extraction, multi-start randomization, and strict constraints.
"""

import time
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from netCDF4 import Dataset, num2date
from scipy.optimize import minimize

from floris import FlorisModel, TimeSeries
from external.landbosse.landbosse.main_function import run_landbosse

# ==========================================
# 1. Geospatial & Site Management
# ==========================================

class SiteManager:
    """
    Handles the loading, normalization, and geometric boundary constraints 
    of the site using geospatial data (.shp).
    """
    def __init__(self, shapefile_path):
        """
        Loads the shapefile and computes the normalization parameters.
        Expected shape: shapefile_path (string)
        """
        self.gdf = gpd.read_file(shapefile_path)
        self.site_polygon = self.gdf.geometry.union_all()
        
        # Origin defined by the most western (min_x) and southern (min_y) points
        self.min_x, self.min_y, self.max_x, self.max_y = self.site_polygon.bounds
        
        # Equal normalization step for both axes
        self.span_x = self.max_x - self.min_x
        self.span_y = self.max_y - self.min_y
        self.scale = max(self.span_x, self.span_y)

    def normalize_coords(self, coords_real):
        """
        Converts real-world coordinates to normalized [0, 1] space.
        Expected shape: coords_real (N, 2)
        """
        coords_norm = np.zeros_like(coords_real, dtype=float)
        coords_norm[:, 0] = (coords_real[:, 0] - self.min_x) / self.scale
        coords_norm[:, 1] = (coords_real[:, 1] - self.min_y) / self.scale
        return coords_norm

    def denormalize_coords(self, coords_norm):
        """
        Converts normalized coordinates back to real-world coordinates.
        Expected shape: coords_norm (N, 2)
        """
        coords_real = np.zeros_like(coords_norm, dtype=float)
        coords_real[:, 0] = (coords_norm[:, 0] * self.scale) + self.min_x
        coords_real[:, 1] = (coords_norm[:, 1] * self.scale) + self.min_y
        return coords_real

    def get_distance_to_boundary(self, x_norm, y_norm):
        """
        Returns the shortest distance from a normalized point to the site boundary.
        Positive if inside, negative if outside. Used for constraint evaluation.
        Expected shapes: x_norm (float), y_norm (float)
        """
        pt_real = self.denormalize_coords(np.array([[x_norm, y_norm]]))[0]
        point = Point(pt_real[0], pt_real[1])
        
        distance_real = self.site_polygon.boundary.distance(point)
        distance_norm = distance_real / self.scale
        
        if self.site_polygon.contains(point):
            return distance_norm
        else:
            return -distance_norm


# ==========================================
# 2. Wind Data Management
# ==========================================

class WindManager:
    """
    Handles the extraction of NetCDF wind data, scaling to hub height via the power law,
    and the generation of the Floris WindRose object.
    """
    def __init__(self, nc_file_path, ref_height_in, hub_height_out, wind_shear, ti, d_ws, d_wd):
        """
        Extracts, formats, and bins wind data directly upon instantiation.
        """
        self.nc_file_path = nc_file_path
        self.ref_height_in = ref_height_in
        self.hub_height_out = hub_height_out
        self.wind_shear = wind_shear
        self.ti = ti
        self.d_ws = d_ws
        self.d_wd = d_wd
        
        self.wind_rose = self._generate_windrose()

    def _generate_windrose(self):
        """
        Internal method to process the .nc file and return the windrose object.
        """
        nc_dataset = Dataset(self.nc_file_path, mode='r')
        
        # Ensure extraction of time and standard 10m wind variables 
        # (Replace 'WS10'/'WD10' if your dataset uses different internal keys)
        time_var = nc_dataset.variables['time']
        times = num2date(time_var[:], time_var.units, calendar=getattr(time_var, 'calendar', 'standard'))
        
        ws_in = np.squeeze(nc_dataset.variables['WS10'][:])
        wd_in = np.squeeze(nc_dataset.variables['WD10'][:])
        nc_dataset.close()
        
        # Power Law Transformation to Hub Height
        ws_hub = ws_in * (self.hub_height_out / self.ref_height_in) ** self.wind_shear
        
        # Build Floris TimeSeries
        timeseries = TimeSeries(wind_speeds=ws_hub, wind_directions=wd_in, turbulence_intensities=self.ti)
        
        # Create WindRose with specified strict discretization (1 deg, 0.5 m/s)
        wind_rose = timeseries.to_WindRose(
            wd_edges=np.arange(0, 360 + self.d_wd, self.d_wd),
            ws_edges=np.arange(0, 50 + self.d_ws, self.d_ws)
        )
        return wind_rose


# ==========================================
# 3. FLORIS Model Management
# ==========================================

class FlorisManager:
    """
    Manages the wake modeling and Annual Energy Production (AEP) calculations.
    """
    def __init__(self, wake_model_path, turbine_type, reference_wind_height, wind_shear, wind_rose):
        self.wake_model_path = wake_model_path
        self.turbine_type = turbine_type
        self.reference_wind_height = reference_wind_height
        self.wind_shear = wind_shear
        self.wind_rose = wind_rose

    def evaluate_layout(self, layout_real):
        """
        Runs the FLORIS model for a given layout (in meters) and returns AEP.
        Expected shape: layout_real (N, 2)
        """
        fmodel = FlorisModel(self.wake_model_path)
        
        fmodel.set(
            layout_x=layout_real[:, 0],
            layout_y=layout_real[:, 1],
            wind_data=self.wind_rose,
            turbine_type=[self.turbine_type],
            reference_wind_height=self.reference_wind_height,
            wind_shear=self.wind_shear
        )
        
        fmodel.run()
        aep_wake = fmodel.get_farm_AEP()
        
        fmodel.run_no_wake()
        aep_no_wake = fmodel.get_farm_AEP()
        
        return aep_wake, aep_no_wake


# ==========================================
# 4. Economics Management
# ==========================================

class EconomicsManager:
    """
    Manages LandBOSSE execution and calculates economic metrics (LCOE, PI).
    """
    def __init__(self, array_voltage, substation_coord, rated_power_kw, 
                 turbine_costs, om_costs, rental_costs, electricity_price, 
                 nominal_discount_rate, project_lifetime):
        
        self.array_voltage = array_voltage
        self.substation_coord = substation_coord
        self.rated_power_kw = rated_power_kw
        self.turbine_costs = turbine_costs
        self.om_costs = om_costs
        self.rental_costs = rental_costs
        self.electricity_price = electricity_price
        self.nominal_discount_rate = nominal_discount_rate
        self.project_lifetime = project_lifetime

    def calculate_metrics(self, layout_real, aep_wh, num_turbines):
        """
        Executes LandBOSSE and calculates economic metrics.
        Expected shapes: layout_real (N, 2), aep_wh (float), num_turbines (int)
        """
        landbosse_df = run_landbosse(
            Turbine_coordinates=layout_real,
            Substation_coordinate=self.substation_coord,
            Desired_Voltage=self.array_voltage,
            WriteExcel=False,
            Display=False
        )
        bos_cost_total = landbosse_df['Cost per project'].sum()
        
        aep_mwh = aep_wh / 1e6
        aep_kwh = aep_wh / 1000
        total_capacity_mw = (self.rated_power_kw / 1000) * num_turbines
        
        turbine_cost_total = self.turbine_costs * total_capacity_mw
        initial_investment = turbine_cost_total + bos_cost_total
        annual_om_cost = (self.om_costs * aep_kwh) + (self.rental_costs * total_capacity_mw)
        
        d = self.nominal_discount_rate
        n = self.project_lifetime
        annuity_factor = ((1 + d)**n - 1) / (d * (1 + d)**n)
        
        lcoe = (initial_investment / (aep_mwh * annuity_factor)) + (annual_om_cost / aep_mwh)
        
        annual_revenue = aep_mwh * self.electricity_price
        net_cash_flow = annual_revenue - annual_om_cost
        pi = (net_cash_flow * annuity_factor) / initial_investment
        
        return pi, lcoe


# ==========================================
# 5. Optimizer Coordinator
# ==========================================

class LayoutOptimizer:
    """
    Runs multi-start layout optimization to maximize PI. Supports dynamic
    turbine counts and boundary-biased random initializations.
    """
    def __init__(self, site_manager, floris_manager, econ_manager, 
                 min_separation_m, opt_method):
        self.site = site_manager
        self.floris = floris_manager
        self.econ = econ_manager
        self.min_dist_norm = min_separation_m / self.site.scale 
        self.opt_method = opt_method
        self.current_num_turbines = None # Set dynamically during loops

    def generate_biased_layout(self, num_turbines, random_seed):
        """
        Generates random layout preferring West/South edges (250° prevailing wind).
        """
        np.random.seed(random_seed)
        layout_norm = []
        max_attempts = 15000
        attempts = 0
        
        while len(layout_norm) < num_turbines and attempts < max_attempts:
            x_cand = np.random.uniform(0, 1)
            y_cand = np.random.uniform(0, 1)
            
            # Must not be directly on the boundary
            dist_to_edge = self.site.get_distance_to_boundary(x_cand, y_cand)
            if dist_to_edge > 0.02: 
                
                # Determine nearest boundary normal vector
                pt_real = self.site.denormalize_coords(np.array([[x_cand, y_cand]]))[0]
                point = Point(pt_real[0], pt_real[1])
                
                # FIX: Use .boundary to project and interpolate safely on MultiPolygons
                boundary_geom = self.site.site_polygon.boundary
                nearest_bound_pt = boundary_geom.interpolate(
                    boundary_geom.project(point)
                )
                
                # If nearest boundary is to the West (dx<0) or South (dy<0), increase acceptance probability
                dx = nearest_bound_pt.x - point.x
                dy = nearest_bound_pt.y - point.y
                is_preferred_edge = (dx < 0) or (dy < 0)
                is_close = dist_to_edge < 0.15 
                
                accept_prob = 1.0 if (is_preferred_edge and is_close) else 0.15
                
                if np.random.rand() < accept_prob:
                    # Enforce 2D separation distance
                    conflict = False
                    for placed_pt in layout_norm:
                        dist = np.sqrt((x_cand - placed_pt[0])**2 + (y_cand - placed_pt[1])**2)
                        if dist < self.min_dist_norm:
                            conflict = True
                            break
                    if not conflict:
                        layout_norm.append([x_cand, y_cand])
            attempts += 1
            
        if len(layout_norm) < num_turbines:
            raise RuntimeError(f"Constraint Failure: Cannot fit {num_turbines} turbines with 2D spacing in site.")
        return np.array(layout_norm)

    def _objective_function(self, layout_flat_norm):
        """
        SciPy objective function (Minimizes -PI).
        """
        layout_norm = layout_flat_norm.reshape(self.current_num_turbines, 2)
        layout_real = self.site.denormalize_coords(layout_norm)
        
        aep_wake, _ = self.floris.evaluate_layout(layout_real)
        pi, _ = self.econ.calculate_metrics(layout_real, aep_wake, self.current_num_turbines)
        
        return -pi

    def run_optimization(self, initial_layout_norm, num_turbines):
        """
        Executes SciPy optimization for a single layout.
        """
        self.current_num_turbines = num_turbines
        x0 = initial_layout_norm.flatten()
        constraints = []
        
        def boundary_constraint(var, idx):
            x, y = var[2 * idx], var[2 * idx + 1]
            return self.site.get_distance_to_boundary(x, y)
            
        for i in range(num_turbines):
            constraints.append({'type': 'ineq', 'fun': boundary_constraint, 'args': (i,)})
            
        def distance_constraint(var, i, j):
            xi, yi = var[2 * i], var[2 * i + 1]
            xj, yj = var[2 * j], var[2 * j + 1]
            return np.sqrt((xi - xj)**2 + (yi - yj)**2) - self.min_dist_norm
            
        for i in range(num_turbines):
            for j in range(i + 1, num_turbines):
                constraints.append({'type': 'ineq', 'fun': distance_constraint, 'args': (i, j)})

        opt_options = {'disp': True, 'maxiter': 50}
        if self.opt_method == 'COBYLA':
            opt_options['rhobeg'] = 0.05

        
        res = minimize(
            fun=self._objective_function, x0=x0, method=self.opt_method,
            constraints=constraints, options=opt_options
        )
        
        return res.x.reshape(num_turbines, 2), -res.fun # Return layout and positive PI

    def run_capacity_top_loop(self, target_mw_min, target_mw_max, num_random_starts):
        """
        Top level loop: iterates through valid turbine counts and performs
        multi-start optimization to find the absolute best overall layout.
        """
        min_turbines = int(np.ceil(target_mw_min / (self.econ.rated_power_kw / 1000)))
        max_turbines = int(np.floor(target_mw_max / (self.econ.rated_power_kw / 1000)))
        
        print(f"Top Loop Range: {min_turbines} to {max_turbines} turbines.")
        
        global_best_pi = -np.inf
        global_best_layout_norm = None
        global_best_n = 0
        global_time = 0
        
        for num_turbines in range(min_turbines, max_turbines + 1):
            print(f"\n--- Testing Capacity: {num_turbines} Turbines ({(num_turbines * 3.37):.2f} MW) ---")
            
            for start_idx in range(num_random_starts):
                seed = int(time.time() * 1000) % 100000 + start_idx
                
                try:
                    init_norm = self.generate_biased_layout(num_turbines, seed)
                except RuntimeError as e:
                    print(f"   [Start {start_idx+1}/{num_random_starts}] Skipping: {e}")
                    continue # Skip if geometrically impossible
                
                print(f"   [Start {start_idx+1}/{num_random_starts}] Optimizing layout...")
                
                t_start = time.time()
                final_norm, best_local_pi = self.run_optimization(init_norm, num_turbines)
                t_end = time.time()
                global_time += (t_end - t_start)
                
                if best_local_pi > global_best_pi:
                    global_best_pi = best_local_pi
                    global_best_layout_norm = final_norm
                    global_best_n = num_turbines
                    print(f"   --> New Best Layout Found! PI: {best_local_pi:.4f}")

        if global_best_layout_norm is None:
            raise RuntimeError("Optimization completely failed. Space may be too restricted.")
            
        return global_best_layout_norm, global_best_n, global_time

    def plot_final_solution(self, final_layout_norm, num_turbines, total_time):
        """
        Plots the ultimate winning layout and evaluates its metrics.
        """
        final_real = self.site.denormalize_coords(final_layout_norm)
        
        aep_wake, aep_nw = self.floris.evaluate_layout(final_real)
        pi, lcoe = self.econ.calculate_metrics(final_real, aep_wake, num_turbines)
        
        eff = (aep_wake / aep_nw) * 100
        cf = aep_wake / (self.econ.rated_power_kw * num_turbines * 1000 * 24 * 365)
        
        fig, ax1 = plt.subplots(1, 1, figsize=(8, 8))
        
        # FIX: Handle plotting for both single Polygons and MultiPolygons safely
        if self.site.site_polygon.geom_type == 'MultiPolygon':
            for geom in self.site.site_polygon.geoms:
                site_x, site_y = geom.exterior.xy
                ax1.plot(site_x, site_y, color='blue')
            # Add proxy artist for legend
            ax1.plot([], [], color='blue', label='Site Boundary')
        elif self.site.site_polygon.geom_type == 'Polygon':
            site_x, site_y = self.site.site_polygon.exterior.xy
            ax1.plot(site_x, site_y, color='blue', label='Site Boundary')
            
        ax1.scatter(self.econ.substation_coord[0, 0], self.econ.substation_coord[0, 1], marker='s', color='orange', s=100, label='Substation')
        ax1.scatter(final_real[:, 0], final_real[:, 1], color='green', s=80, label='Optimized Turbines')
        
        ax1.set_aspect('equal')
        ax1.set_xlabel('Easting [m]')
        ax1.set_ylabel('Northing [m]')
        ax1.set_title(f'Ultimate Optimal Wind Farm (N={num_turbines})')
        ax1.legend()
        ax1.grid(True)
        
        results_text = (
            f"--- GLOBAL OPTIMUM FOUND ---\n"
            f"Turbines: {num_turbines} ({(num_turbines * 3.37):.2f} MW)\n"
            f"Total Compute Time: {total_time:.2f} s\n"
            f"Final PI: {pi:.4f}\n"
            f"Final LCoE: {lcoe:.2f} $/MWh\n"
            f"Final AEP: {aep_wake/1e9:.4f} GWh\n"
            f"Farm Efficiency: {eff:.2f}%\n"
            f"Capacity Factor: {cf:.4f}"
        )
        
        plt.figtext(0.5, 0.01, results_text, wrap=True, horizontalalignment='center', fontsize=11,
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.9))
                    
        plt.subplots_adjust(bottom=0.25)
        plt.show()


# ==========================================
# 6. Main Execution Pipeline
# ==========================================

if __name__ == "__main__":
    
    # ------------------ Inputs ------------------
    SHAPEFILE_PATH = "selected_site_schlegelmuehle/ausgewahlflächen_schlegelmuehle.shp"
    NC_FILE_PATH = "essai10_schlegelmuehle.nc"
    
    TURBINE_DIAMETER = 130 # meters
    MIN_DISTANCE_M = 2 * TURBINE_DIAMETER
    RATED_POWER_KW = 3370
    
    TARGET_MIN_MW = 45
    TARGET_MAX_MW = 60
    NUM_RANDOM_STARTS = 3 # Increase for heavier exploration
    
    # Substation coordinate must be evaluated/placed prior based on site geometry
    SUBSTATION_COORD = np.array([[694264.9, 5570861.7]]) # EPSG 25832 (UTM Zone 32N)
    # --------------------------------------------
    
    try:
        site_mgr = SiteManager(shapefile_path=SHAPEFILE_PATH)
        
        wind_mgr = WindManager(
            nc_file_path=NC_FILE_PATH,
            ref_height_in=10,
            hub_height_out=120,
            wind_shear=0.2,
            ti=0.06,
            d_ws=0.5,
            d_wd=1
        )
        
        floris_mgr = FlorisManager(
            wake_model_path=r"inputs/gch.yaml",
            turbine_type="IEA3_4_MW",
            reference_wind_height=120,
            wind_shear=0.2,
            wind_rose=wind_mgr.wind_rose 
        )
        
        econ_mgr = EconomicsManager(
            array_voltage=30,
            substation_coord=SUBSTATION_COORD,
            rated_power_kw=RATED_POWER_KW,
            turbine_costs=1.3 * 1e6,
            om_costs=0.016,
            rental_costs=20000,
            electricity_price=67,
            nominal_discount_rate=0.04,
            project_lifetime=20
        )
        
        optimizer = LayoutOptimizer(
            site_manager=site_mgr,
            floris_manager=floris_mgr,
            econ_manager=econ_mgr,
            min_separation_m=MIN_DISTANCE_M,
            opt_method='COBYLA' # Switch to SLSQP if desired
        )
        
        # Execute Top-Level Loop
        best_layout_norm, best_n, comp_time = optimizer.run_capacity_top_loop(
            target_mw_min=TARGET_MIN_MW, 
            target_mw_max=TARGET_MAX_MW, 
            num_random_starts=NUM_RANDOM_STARTS
        )
        
        # Output final overall results
        optimizer.plot_final_solution(best_layout_norm, best_n, comp_time)
        
    except Exception as e:
        import traceback
        print(f"Execution failed: {e}")
        traceback.print_exc()