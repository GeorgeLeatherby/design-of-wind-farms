"""
final_assignment.py

Optimization of Wind Farm Layout for the Bavaria Site (Schlegelmuehle).
Maximizes Profitability Index (PI) across variable turbine counts (45-60 MW).
Includes NetCDF wind data extraction, multi-start randomization, and strict constraints.
"""

import time
import secrets
import json
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from netCDF4 import Dataset, num2date
from scipy.optimize import minimize

from floris import FlorisModel, TimeSeries
from floris.flow_visualization import visualize_cut_plane
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
    def __init__(self, nc_file_path, ref_height_in, hub_height_out, wind_shear, ti,
                 discretization_aep, discretization_pi):
        """
        Extracts, formats, and bins wind data directly upon instantiation.
        """
        self.nc_file_path = nc_file_path
        self.ref_height_in = ref_height_in
        self.hub_height_out = hub_height_out
        self.wind_shear = wind_shear
        self.ti = ti
        self.discretization_aep = discretization_aep
        self.discretization_pi = discretization_pi
        self.dominant_wind_speed = None
        self.dominant_wind_direction = None
        self.mean_hub_wind_speed = None
        
        self.wind_rose_aep = self._generate_windrose(self.discretization_aep)
        self.wind_rose_pi = self._generate_windrose(self.discretization_pi)

    def _set_dominant_wind_bin(self, ws_hub, wd_in, discretization):
        """
        Finds the most frequent (ws, wd) bin using the same discretization
        used for the wind rose.
        """
        d_ws = discretization.get('d_ws') if discretization is not None else None
        d_wd = discretization.get('d_wd') if discretization is not None else None
        wd_wrapped = np.mod(wd_in, 360.0)
        ws_edges = np.arange(0, 50 + d_ws, d_ws)
        wd_edges = np.arange(0, 360 + d_wd, d_wd)

        hist, ws_bin_edges, wd_bin_edges = np.histogram2d(
            ws_hub,
            wd_wrapped,
            bins=[ws_edges, wd_edges]
        )

        if np.sum(hist) <= 0:
            self.dominant_wind_speed = float(np.mean(ws_hub))
            self.dominant_wind_direction = float(np.mean(wd_wrapped))
            return

        i_ws, i_wd = np.unravel_index(np.argmax(hist), hist.shape)
        self.dominant_wind_speed = 0.5 * (ws_bin_edges[i_ws] + ws_bin_edges[i_ws + 1])
        self.dominant_wind_direction = 0.5 * (wd_bin_edges[i_wd] + wd_bin_edges[i_wd + 1])

    def _generate_windrose(self, discretization):
        """
        Internal method to process the .nc file and return the windrose object.
        """
        d_ws = discretization.get('d_ws') if discretization is not None else None
        d_wd = discretization.get('d_wd') if discretization is not None else None
        nc_dataset = Dataset(self.nc_file_path, mode='r')
        
        # Ensure extraction of time and standard 10m wind variables 
        time_var = nc_dataset.variables['time']
        times = num2date(time_var[:], time_var.units, calendar=getattr(time_var, 'calendar', 'standard'))
        
        ws_in = np.squeeze(nc_dataset.variables['WS10'][:])
        wd_in = np.squeeze(nc_dataset.variables['WD10'][:])
        nc_dataset.close()
        
        # Power Law Transformation to Hub Height
        ws_hub = ws_in * (self.hub_height_out / self.ref_height_in) ** self.wind_shear
        self.mean_hub_wind_speed = float(np.mean(ws_hub))
        self._set_dominant_wind_bin(ws_hub, wd_in, self.discretization_pi)
        
        # Build Floris TimeSeries
        timeseries = TimeSeries(wind_speeds=ws_hub, wind_directions=wd_in, turbulence_intensities=self.ti)
        
        # Create WindRose with stage-specific discretization.
        wind_rose = timeseries.to_WindRose(
            wd_edges=np.arange(0, 360 + d_wd, d_wd),
            ws_edges=np.arange(0, 50 + d_ws, d_ws)
        )
        return wind_rose


# ==========================================
# 3. FLORIS Model Management
# ==========================================

class FlorisManager:
    """
    Manages the wake modeling and Annual Energy Production (AEP) calculations.
    """
    def __init__(
        self,
        wake_model_path,
        turbine_type,
        reference_wind_height,
        wind_shear,
        wind_rose_aep,
        wind_rose_pi,
        dominant_wind_speed=None,
        dominant_wind_direction=None
    ):
        self.wake_model_path = wake_model_path
        self.turbine_type = turbine_type
        self.reference_wind_height = reference_wind_height
        self.wind_shear = wind_shear
        self.wind_rose_aep = wind_rose_aep
        self.wind_rose_pi = wind_rose_pi
        self.dominant_wind_speed = dominant_wind_speed
        self.dominant_wind_direction = dominant_wind_direction
        self.fmodel = FlorisModel(self.wake_model_path)

    def evaluate_layout_aep(self, layout_real):
        """
        Runs FLORIS with the AEP-stage wind rose and returns wake AEP only.
        Expected shape: layout_real (N, 2)
        """
        self.fmodel.set(
            layout_x=layout_real[:, 0],
            layout_y=layout_real[:, 1],
            wind_data=self.wind_rose_aep,
            turbine_type=[self.turbine_type],
            reference_wind_height=self.reference_wind_height,
            wind_shear=self.wind_shear
        )

        self.fmodel.run()
        return self.fmodel.get_farm_AEP()

    def evaluate_layout_pi(self, layout_real):
        """
        Runs FLORIS with the PI-stage wind rose and returns wake/no-wake AEP.
        Expected shape: layout_real (N, 2)
        """
        self.fmodel.set(
            layout_x=layout_real[:, 0],
            layout_y=layout_real[:, 1],
            wind_data=self.wind_rose_pi,
            turbine_type=[self.turbine_type],
            reference_wind_height=self.reference_wind_height,
            wind_shear=self.wind_shear
        )

        self.fmodel.run()
        aep_wake = self.fmodel.get_farm_AEP()

        self.fmodel.run_no_wake()
        aep_no_wake = self.fmodel.get_farm_AEP()

        return aep_wake, aep_no_wake

    def plot_final_wake_top_view(
        self,
        layout_real,
        site_polygon=None,
        wind_speed=None,
        wind_direction=None,
        turbulence_intensity=0.06,
        x_resolution=250,
        y_resolution=250
    ):
        """
        Plots a top-view wake field for the final layout at one representative
        operating point using FLORIS cut-plane visualization.
        """
        if wind_speed is None:
            wind_speed = self.dominant_wind_speed if self.dominant_wind_speed is not None else 8.0
        if wind_direction is None:
            wind_direction = self.dominant_wind_direction if self.dominant_wind_direction is not None else 240.0

        num_turbines = layout_real.shape[0]

        # Use a dedicated model for visualization so we do not overwrite
        # the optimization model state (and avoid wind_data reset warnings).
        viz_fmodel = FlorisModel(self.wake_model_path)
        viz_fmodel.set(
            layout_x=layout_real[:, 0],
            layout_y=layout_real[:, 1],
            wind_speeds=[wind_speed],
            wind_directions=[wind_direction],
            turbulence_intensities=[turbulence_intensity],
            turbine_type=[self.turbine_type] * num_turbines,
            reference_wind_height=self.reference_wind_height,
            wind_shear=self.wind_shear
        )
        viz_fmodel.run()

        horizontal_plane = viz_fmodel.calculate_horizontal_plane(
            height=self.reference_wind_height,
            x_resolution=x_resolution,
            y_resolution=y_resolution,
            findex_for_viz=0
        )

        fig, ax = plt.subplots(1, 1, figsize=(9, 7))
        visualize_cut_plane(
            horizontal_plane,
            ax=ax,
            title=(
                f"Wake Top View at Hub Height ({self.reference_wind_height:.0f} m), "
                f"WD={wind_direction:.1f} deg, WS={wind_speed:.1f} m/s"
            ),
            color_bar=True
        )
        ax.scatter(
            layout_real[:, 0],
            layout_real[:, 1],
            marker='o',
            s=40,
            facecolors='none',
            edgecolors='black',
            linewidths=1.0,
            label='Turbine Locations'
        )

        if site_polygon is not None:
            if site_polygon.geom_type == 'MultiPolygon':
                for geom in site_polygon.geoms:
                    site_x, site_y = geom.exterior.xy
                    ax.plot(site_x, site_y, color='white', linewidth=1.6, alpha=0.95)
                ax.plot([], [], color='white', linewidth=1.6, label='Site Boundary')
            elif site_polygon.geom_type == 'Polygon':
                site_x, site_y = site_polygon.exterior.xy
                ax.plot(site_x, site_y, color='white', linewidth=1.6, alpha=0.95, label='Site Boundary')

        ax.set_aspect('equal')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.25)
        fig.tight_layout()


# ==========================================
# 4. Economics Management
# ==========================================

class EconomicsManager:
    """
    Manages LandBOSSE execution and calculates economic metrics (LCOE, PI).
    """
    def __init__(self, array_voltage, substation_coord, rated_power_kw,
                 turbine_costs, om_costs, rental_costs,
                 nominal_discount_rate, project_lifetime,
                 electricity_price_model, project_start_year,
                 hub_height, wind_speed_hub, theta_shear):
        
        self.array_voltage = array_voltage
        self.substation_coord = substation_coord
        self.rated_power_kw = rated_power_kw
        self.turbine_costs = turbine_costs
        self.om_costs = om_costs
        self.rental_costs = rental_costs
        self.nominal_discount_rate = nominal_discount_rate
        self.project_lifetime = project_lifetime
        self.electricity_price_model = electricity_price_model
        self.project_start_year = project_start_year
        self.hub_height = hub_height
        self.wind_speed_hub = wind_speed_hub
        self.theta_shear = theta_shear

    def _get_spot_price_for_year(self, year):
        annual_average_price = self.electricity_price_model.get('annual_average_price_by_year_usd_per_mwh') if self.electricity_price_model is not None else None
        site_coefficient = self.electricity_price_model.get('site_coefficient') if self.electricity_price_model is not None else None
        site_wind_factor = self.electricity_price_model.get('site_wind_factor') if self.electricity_price_model is not None else None
        reference_hub_height = self.electricity_price_model.get('reference_hub_height_m') if self.electricity_price_model is not None else None

        A = annual_average_price.get(str(year)) if annual_average_price is not None else None
        wind_term = site_wind_factor * ((reference_hub_height / self.hub_height) ** self.theta_shear) * self.wind_speed_hub
        return A * (site_coefficient - wind_term)

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
        discounted_energy_total = 0.0
        discounted_om_total = 0.0
        discounted_net_cash_flow_total = 0.0

        for year_offset in range(n):
            year = self.project_start_year + year_offset
            spot_price = self._get_spot_price_for_year(year)
            annual_revenue = aep_mwh * spot_price
            annual_net_cash_flow = annual_revenue - annual_om_cost
            discount_factor = 1.0 / ((1.0 + d) ** (year_offset + 1))

            discounted_energy_total += aep_mwh * discount_factor
            discounted_om_total += annual_om_cost * discount_factor
            discounted_net_cash_flow_total += annual_net_cash_flow * discount_factor

        lcoe = (initial_investment + discounted_om_total) / discounted_energy_total
        pi = discounted_net_cash_flow_total / initial_investment
        
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
                 min_separation_m, opt_method, verbose=True, objective_log_every=5):
        self.site = site_manager
        self.floris = floris_manager
        self.econ = econ_manager
        self.min_dist_norm = min_separation_m / self.site.scale
        self.opt_method = opt_method
        self.current_num_turbines = None # Set dynamically during loops
        self.verbose = verbose
        self.objective_log_every = objective_log_every
        self.obj_eval_count = 0
        self.best_eval_pi = -np.inf
        self.best_eval_aep = -np.inf
        self.current_run_history_norm = []
        self.last_run_history_norm = []

    @staticmethod
    def _unique_rows(arr, decimals=8):
        """
        Removes duplicate 2D points with rounding tolerance.
        """
        if arr.size == 0:
            return arr
        rounded = np.round(arr, decimals=decimals)
        _, idx = np.unique(rounded, axis=0, return_index=True)
        return arr[np.sort(idx)]

    def _log(self, msg):
        if self.verbose:
            print(msg)

    def _is_valid_point(self, cand_norm, placed_norm):
        """
        Checks polygon and minimum-distance feasibility of a candidate point.
        """
        if self.site.get_distance_to_boundary(cand_norm[0], cand_norm[1]) <= 0.0:
            return False

        for placed_pt in placed_norm:
            if np.linalg.norm(cand_norm - placed_pt) < self.min_dist_norm:
                return False

        return True

    def _iter_polygon_parts(self, geom):
        """
        Returns a list of polygons from Polygon/MultiPolygon geometries.
        """
        if geom.geom_type == 'Polygon':
            return [geom]
        if geom.geom_type == 'MultiPolygon':
            return list(geom.geoms)
        return []

    def _generate_edge_candidates(self, rng, edge_offset_norm):
        """
        Generates near-edge candidate points from an inward polygon buffer.
        """
        edge_offset_real = edge_offset_norm * self.site.scale
        inner_geom = self.site.site_polygon.buffer(-edge_offset_real)
        if inner_geom.is_empty:
            inner_geom = self.site.site_polygon

        candidates = []
        target_spacing_norm = max(self.min_dist_norm * 1.05, edge_offset_norm * 2.0)

        for poly in self._iter_polygon_parts(inner_geom):
            boundary = poly.exterior
            perimeter_real = boundary.length
            perimeter_norm = perimeter_real / self.site.scale
            n_candidates = max(1, int(np.floor(perimeter_norm / target_spacing_norm)))
            phase = rng.uniform(0.0, 1.0)

            for idx in range(n_candidates):
                s = ((idx + phase) / n_candidates) * perimeter_real
                point_real = boundary.interpolate(s % perimeter_real)
                cand_norm = np.array([
                    (point_real.x - self.site.min_x) / self.site.scale,
                    (point_real.y - self.site.min_y) / self.site.scale
                ])
                candidates.append(cand_norm)

        if len(candidates) == 0:
            return np.empty((0, 2), dtype=float)

        return np.array(candidates)

    def _sample_random_inside(self, rng):
        """
        Samples one random normalized point from the site bounding box.
        """
        x_cand = rng.uniform(0.0, 1.0)
        y_cand = rng.uniform(0.0, 1.0)
        return np.array([x_cand, y_cand], dtype=float)

    def generate_initial_layout(self, num_turbines, rng, edge_offset_norm=0.01, max_random_attempts=100):
        """
        Two-tier initial solution generator:
        1) Place turbines quasi-uniformly along interior edges.
        2) Fill remaining turbines with random interior placement.
        """
        self._log(
            f"      [Init] Searching feasible initial layout for N={num_turbines} "
            f"(edge_offset_norm={edge_offset_norm:.3f}, random_try_limit={max_random_attempts})"
        )
        layout_norm = []
        viable_edge_candidates = []
        selected_edge_positions = []

        edge_candidates = self._generate_edge_candidates(rng, edge_offset_norm=edge_offset_norm)
        self._log(f"      [Init] Edge tier generated {edge_candidates.shape[0]} candidates.")
        if edge_candidates.shape[0] > 0:
            remaining_candidates = [edge_candidates[i] for i in rng.permutation(edge_candidates.shape[0])]
            while len(layout_norm) < num_turbines and len(remaining_candidates) > 0:
                viable_indices = [
                    idx for idx, cand_norm in enumerate(remaining_candidates)
                    if self._is_valid_point(cand_norm, layout_norm)
                ]
                if len(viable_indices) > 0:
                    viable_edge_candidates.extend([remaining_candidates[idx].copy() for idx in viable_indices])
                if len(viable_indices) == 0:
                    break

                pick_pos = int(rng.integers(0, len(viable_indices)))
                selected_idx = viable_indices[pick_pos]
                chosen = remaining_candidates.pop(selected_idx)
                selected_edge_positions.append(chosen.copy())
                layout_norm.append(chosen)

        self._log(
            f"      [Init] Edge tier placed {len(layout_norm)}/{num_turbines} turbines."
        )

        random_attempts = 0
        while len(layout_norm) < num_turbines and random_attempts < max_random_attempts:
            cand_norm = self._sample_random_inside(rng)
            random_attempts += 1
            if self._is_valid_point(cand_norm, layout_norm):
                layout_norm.append(cand_norm)

        self._log(
            f"      [Init] Random tier used {random_attempts} tries and reached "
            f"{len(layout_norm)}/{num_turbines} turbines."
        )

        if len(layout_norm) < num_turbines:
            raise RuntimeError(
                f"Initial solution failed: could not place all {num_turbines} turbines "
                f"inside polygon boundaries with >=2D spacing after {max_random_attempts} random tries."
            )

        self._log("      [Init] Feasible initial layout found.")

        edge_candidates_arr = np.array(edge_candidates) if edge_candidates.size else np.empty((0, 2), dtype=float)
        viable_edge_arr = np.array(viable_edge_candidates) if len(viable_edge_candidates) > 0 else np.empty((0, 2), dtype=float)
        selected_edge_arr = np.array(selected_edge_positions) if len(selected_edge_positions) > 0 else np.empty((0, 2), dtype=float)

        init_debug = {
            'edge_candidates_norm': edge_candidates_arr,
            'viable_edge_candidates_norm': self._unique_rows(viable_edge_arr),
            'selected_edge_positions_norm': self._unique_rows(selected_edge_arr)
        }

        return np.array(layout_norm), init_debug

    def _layout_is_feasible(self, layout_norm):
        """
        Fast feasibility check to avoid evaluating clearly invalid layouts.
        """
        for i in range(layout_norm.shape[0]):
            if self.site.get_distance_to_boundary(layout_norm[i, 0], layout_norm[i, 1]) <= 0.0:
                return False

        for i in range(layout_norm.shape[0]):
            for j in range(i + 1, layout_norm.shape[0]):
                if np.linalg.norm(layout_norm[i] - layout_norm[j]) < self.min_dist_norm:
                    return False

        return True

    def _objective_function(self, layout_flat_norm):
        """
        SciPy objective function (Minimizes -PI).
        """
        self.obj_eval_count += 1
        layout_norm = layout_flat_norm.reshape(self.current_num_turbines, 2)
        self.current_run_history_norm.append(layout_norm.copy())
        if not self._layout_is_feasible(layout_norm):
            return 10 # Large penalty for infeasibility

        layout_real = self.site.denormalize_coords(layout_norm)
        
        aep_wake, _ = self.floris.evaluate_layout_pi(layout_real)
        pi, _ = self.econ.calculate_metrics(layout_real, aep_wake, self.current_num_turbines)

        if pi > self.best_eval_pi:
            self.best_eval_pi = pi

        if self.objective_log_every > 0 and (self.obj_eval_count % self.objective_log_every == 0):
            self._log(
                f"      [Opt] Eval {self.obj_eval_count}: PI={pi:.4f}, best_eval_PI={self.best_eval_pi:.4f}"
            )
        
        return -pi

    def _aep_objective_function(self, layout_flat_norm):
        """
        SciPy objective function (Minimizes -AEP).
        """
        self.obj_eval_count += 1
        layout_norm = layout_flat_norm.reshape(self.current_num_turbines, 2)
        self.current_run_history_norm.append(layout_norm.copy())
        if not self._layout_is_feasible(layout_norm):
            return 10

        layout_real = self.site.denormalize_coords(layout_norm)
        aep_wake = self.floris.evaluate_layout_aep(layout_real)

        if aep_wake > self.best_eval_aep:
            self.best_eval_aep = aep_wake

        if self.objective_log_every > 0 and (self.obj_eval_count % self.objective_log_every == 0):
            self._log(
                f"      [AEP] Eval {self.obj_eval_count}: AEP={aep_wake/1e9:.4f} GWh, "
                f"best_eval_AEP={self.best_eval_aep/1e9:.4f} GWh"
            )

        return -aep_wake

    def _build_constraints(self, num_turbines):
        constraints = []

        def boundary_constraint(var, idx):
            x, y = var[2 * idx], var[2 * idx + 1]
            return self.site.get_distance_to_boundary(x, y)

        def lower_x_constraint(var, idx):
            return var[2 * idx]

        def upper_x_constraint(var, idx):
            return 1.0 - var[2 * idx]

        def lower_y_constraint(var, idx):
            return var[2 * idx + 1]

        def upper_y_constraint(var, idx):
            return 1.0 - var[2 * idx + 1]

        for i in range(num_turbines):
            constraints.append({'type': 'ineq', 'fun': boundary_constraint, 'args': (i,)})
            constraints.append({'type': 'ineq', 'fun': lower_x_constraint, 'args': (i,)})
            constraints.append({'type': 'ineq', 'fun': upper_x_constraint, 'args': (i,)})
            constraints.append({'type': 'ineq', 'fun': lower_y_constraint, 'args': (i,)})
            constraints.append({'type': 'ineq', 'fun': upper_y_constraint, 'args': (i,)})

        def distance_constraint(var, i, j):
            xi, yi = var[2 * i], var[2 * i + 1]
            xj, yj = var[2 * j], var[2 * j + 1]
            return np.sqrt((xi - xj)**2 + (yi - yj)**2) - self.min_dist_norm

        for i in range(num_turbines):
            for j in range(i + 1, num_turbines):
                constraints.append({'type': 'ineq', 'fun': distance_constraint, 'args': (i, j)})

        return constraints

    def _build_opt_options(self):
        opt_options = {'disp': True, 'maxiter': 200}
        if self.opt_method == 'COBYLA':
            opt_options['rhobeg'] = 0.08
            opt_options['catol'] = 1e-4
            opt_options['tol'] = 5e-4
        return opt_options

    def _run_optimization_stage(self, initial_layout_norm, num_turbines, objective_function, stage_label):
        self.current_num_turbines = num_turbines
        self.obj_eval_count = 0
        self.best_eval_pi = -np.inf
        self.best_eval_aep = -np.inf
        self.current_run_history_norm = [initial_layout_norm.copy()]
        x0 = initial_layout_norm.flatten()
        constraints = self._build_constraints(num_turbines)
        opt_options = self._build_opt_options()

        self._log(
            f"      [{stage_label}] Starting {self.opt_method} for N={num_turbines} with "
            f"{len(constraints)} constraints."
        )

        res = minimize(
            fun=objective_function,
            x0=x0,
            method=self.opt_method,
            constraints=constraints,
            options=opt_options
        )

        self.last_run_history_norm = [step.copy() for step in self.current_run_history_norm]
        return res

    def run_optimization(self, initial_layout_norm, num_turbines):
        """
        Executes SciPy optimization for a single layout.
        """
        res = self._run_optimization_stage(
            initial_layout_norm=initial_layout_norm,
            num_turbines=num_turbines,
            objective_function=self._objective_function,
            stage_label='PI'
        )

        self._log(
            f"      [Opt] Finished {self.opt_method}: success={res.success}, "
            f"status={res.status}, nfev={getattr(res, 'nfev', 'n/a')}, "
            f"best_local_PI={-res.fun:.4f}"
        )
        
        return res.x.reshape(num_turbines, 2), -res.fun # Return layout and positive PI

    def run_aep_optimization(self, initial_layout_norm, num_turbines):
        """
        Executes SciPy optimization for a single layout using AEP only.
        """
        res = self._run_optimization_stage(
            initial_layout_norm=initial_layout_norm,
            num_turbines=num_turbines,
            objective_function=self._aep_objective_function,
            stage_label='AEP'
        )

        self._log(
            f"      [AEP] Finished {self.opt_method}: success={res.success}, "
            f"status={res.status}, nfev={getattr(res, 'nfev', 'n/a')}, "
            f"best_local_AEP={-res.fun/1e9:.4f} GWh"
        )

        return res.x.reshape(num_turbines, 2), -res.fun

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
        global_best_init_layout_norm = None
        global_best_n = 0
        global_best_init_debug = None
        global_time = 0
        
        for num_turbines in range(min_turbines, max_turbines + 1):
            print(f"\n--- Testing Capacity: {num_turbines} Turbines ({(num_turbines * 3.37):.2f} MW) ---")
            capacity_best = -np.inf
            aep_candidates = []
            
            for start_idx in range(num_random_starts):
                seed = secrets.randbits(64)
                rng = np.random.default_rng(seed)
                print(f"   [Start {start_idx+1}/{num_random_starts}] Seed: {seed}")
                print(f"   [Start {start_idx+1}/{num_random_starts}] Building initial layout...")
                
                try:
                    init_norm, init_debug = self.generate_initial_layout(num_turbines, rng)
                except RuntimeError as e:
                    print(f"   [Start {start_idx+1}/{num_random_starts}] Skipping: {e}")
                    continue # Skip if geometrically impossible

                print(
                    f"   [Start {start_idx+1}/{num_random_starts}] Initial layout accepted. "
                    f"Launching AEP optimization..."
                )

                t_start = time.time()
                aep_layout_norm, best_local_aep = self.run_aep_optimization(init_norm, num_turbines)
                t_end = time.time()
                global_time += (t_end - t_start)

                print(
                    f"   [Start {start_idx+1}/{num_random_starts}] Done in {t_end - t_start:.2f}s, "
                    f"AEP={best_local_aep/1e9:.4f} GWh"
                )

                aep_candidates.append({
                    'aep': best_local_aep,
                    'layout_norm': aep_layout_norm.copy(),
                    'init_norm': init_norm.copy(),
                    'init_debug': init_debug
                })

            if len(aep_candidates) == 0:
                print(f"--- Capacity Summary N={num_turbines}: no feasible initial layout found. ---")
                continue

            aep_candidates.sort(key=lambda candidate: candidate['aep'], reverse=True)
            pi_finalists = aep_candidates[:5]

            print(
                f"   [AEP] Selected {len(pi_finalists)} layouts for PI optimization "
                f"from {len(aep_candidates)} AEP-optimized candidates."
            )

            for finalist_idx, finalist in enumerate(pi_finalists):
                print(
                    f"   [PI {finalist_idx+1}/{len(pi_finalists)}] Optimizing AEP finalist "
                    f"with AEP={finalist['aep']/1e9:.4f} GWh..."
                )

                t_start = time.time()
                final_norm, best_local_pi = self.run_optimization(finalist['layout_norm'], num_turbines)
                t_end = time.time()
                global_time += (t_end - t_start)

                print(
                    f"   [PI {finalist_idx+1}/{len(pi_finalists)}] Done in {t_end - t_start:.2f}s, "
                    f"PI={best_local_pi:.4f}"
                )

                capacity_best = max(capacity_best, best_local_pi)

                if best_local_pi > global_best_pi:
                    global_best_pi = best_local_pi
                    global_best_layout_norm = final_norm
                    global_best_init_layout_norm = finalist['init_norm'].copy()
                    global_best_n = num_turbines
                    global_best_init_debug = finalist['init_debug']
                    print(f"   --> New Best Layout Found! PI: {best_local_pi:.4f}")

            if capacity_best > -np.inf:
                print(
                    f"--- Capacity Summary N={num_turbines}: best PI={capacity_best:.4f}, "
                    f"global best PI={global_best_pi:.4f} ---"
                )

        if global_best_layout_norm is None:
            raise RuntimeError("Optimization completely failed. Space may be too restricted.")
            
        return global_best_layout_norm, global_best_init_layout_norm, global_best_init_debug, global_best_n, global_time

    def plot_final_solution(self, final_layout_norm, initial_layout_norm, init_debug, num_turbines, total_time):
        """
        Plots the ultimate winning layout and evaluates its metrics.
        Also adds a wake top-view and a diagnostics figure with coordinate table.
        """
        final_real = self.site.denormalize_coords(final_layout_norm)
        init_real = self.site.denormalize_coords(initial_layout_norm)
        
        aep_wake, aep_nw = self.floris.evaluate_layout_pi(final_real)
        pi, lcoe = self.econ.calculate_metrics(final_real, aep_wake, num_turbines)
        
        eff = (aep_wake / aep_nw) * 100
        cf = aep_wake / (self.econ.rated_power_kw * num_turbines * 1000 * 24 * 365)
        
        fig, ax1 = plt.subplots(1, 1, figsize=(8, 8))
        
        # Handle plotting for both single Polygons and MultiPolygons safely
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
        ax1.scatter(
            init_real[:, 0],
            init_real[:, 1],
            marker='x',
            color='gray',
            s=65,
            alpha=0.95,
            linewidths=1.5,
            label='Initial Turbines',
            zorder=5
        )
        
        ax1.set_aspect('equal')
        ax1.set_xlabel('East [m]')
        ax1.set_ylabel('North [m]')
        ax1.set_title(f'Optimal Wind Farm (N={num_turbines})')
        ax1.legend()
        ax1.grid(True)
        
        results_text = (
            f"--- OPTIMUM FOUND ---\n"
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

        # Plot 2: FLORIS top-view wake map for the final layout.
        self.floris.plot_final_wake_top_view(final_real, site_polygon=self.site.site_polygon)

        # Plot 3: Coordinates table + tier-1 viable edge candidates diagnostics.
        fig3, (ax_tbl, ax_map) = plt.subplots(
            2,
            1,
            figsize=(13, 12),
            gridspec_kw={'height_ratios': [2, 3]}
        )
        ax_tbl.axis('off')
        table_rows = [
            [
                i + 1,
                f"{init_real[i, 0]:.2f}",
                f"{init_real[i, 1]:.2f}",
                f"{final_real[i, 0]:.2f}",
                f"{final_real[i, 1]:.2f}"
            ]
            for i in range(num_turbines)
        ]
        table = ax_tbl.table(
            cellText=table_rows,
            colLabels=['Turbine', 'Start X [m]', 'Start Y [m]', 'Final X [m]', 'Final Y [m]'],
            loc='center'
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.0, 1.2)
        ax_tbl.set_title('Turbine Coordinates: Start vs Final (Best Solution)')

        if self.site.site_polygon.geom_type == 'MultiPolygon':
            for geom in self.site.site_polygon.geoms:
                site_x, site_y = geom.exterior.xy
                ax_map.plot(site_x, site_y, color='blue')
            ax_map.plot([], [], color='blue', label='Site Boundary')
        elif self.site.site_polygon.geom_type == 'Polygon':
            site_x, site_y = self.site.site_polygon.exterior.xy
            ax_map.plot(site_x, site_y, color='blue', label='Site Boundary')

        viable_edge_norm = init_debug['viable_edge_candidates_norm'] if init_debug is not None else np.empty((0, 2), dtype=float)
        if viable_edge_norm.size > 0:
            viable_edge_real = self.site.denormalize_coords(viable_edge_norm)
            ax_map.scatter(
                viable_edge_real[:, 0],
                viable_edge_real[:, 1],
                marker='.',
                s=18,
                alpha=0.45,
                color='tab:blue',
                label=f"Tier-1 Viable Candidates (n={viable_edge_real.shape[0]})"
            )

        ax_map.scatter(init_real[:, 0], init_real[:, 1], marker='x', s=55, color='gray', label='Initial Turbines')
        ax_map.scatter(final_real[:, 0], final_real[:, 1], marker='o', s=35, color='green', label='Final Turbines')
        ax_map.scatter(self.econ.substation_coord[0, 0], self.econ.substation_coord[0, 1], marker='s', color='orange', s=80, label='Substation')
        ax_map.set_aspect('equal')
        ax_map.set_xlabel('East [m]')
        ax_map.set_ylabel('North [m]')
        ax_map.set_title('Tier-1 Viable Boundary Candidates and Best Layout Coordinates')
        ax_map.grid(True, alpha=0.35)
        ax_map.legend(loc='best')
        fig3.tight_layout()

        plt.show()


# ==========================================
# 6. Main Execution Pipeline
# ==========================================

if __name__ == "__main__":
    CONFIG_PATH = "configs/schlegelmuehle.json" # Hier den Pfad zur gewünschten Konfigurationsdatei angeben

    with open(CONFIG_PATH, mode='r', encoding='utf-8') as config_file:
        config = json.load(config_file)

    site_config = config.get('site')
    wind_config = config.get('wind')
    turbine_config = config.get('turbine')
    optimization_config = config.get('optimization')
    substation_config = config.get('substation')
    floris_config = config.get('floris')
    economics_config = config.get('economics')
    # Expected shape: {'aep': {'d_wd': float, 'd_ws': float}, 'pi': {'d_wd': float, 'd_ws': float}}
    wind_discretization_config = wind_config.get('discretization') if wind_config is not None else None
    aep_discretization_config = wind_discretization_config.get('aep') if wind_discretization_config is not None else None
    pi_discretization_config = wind_discretization_config.get('pi') if wind_discretization_config is not None else None

    shapefile_path = site_config.get('shapefile_path') if site_config is not None else None
    nc_file_path = wind_config.get('nc_file_path') if wind_config is not None else None
    turbine_diameter = turbine_config.get('diameter_m') if turbine_config is not None else None
    rated_power_kw = turbine_config.get('rated_power_kw') if turbine_config is not None else None
    min_distance_multiplier = optimization_config.get('min_distance_multiplier') if optimization_config is not None else None
    min_distance_m = (
        min_distance_multiplier * turbine_diameter
        if min_distance_multiplier is not None and turbine_diameter is not None
        else None
    )
    target_min_mw = optimization_config.get('target_min_mw') if optimization_config is not None else None
    target_max_mw = optimization_config.get('target_max_mw') if optimization_config is not None else None
    num_random_starts = optimization_config.get('num_random_starts') if optimization_config is not None else None
    substation_coord = (
        np.array(substation_config.get('coordinates'))
        if substation_config is not None and substation_config.get('coordinates') is not None
        else None
    )
    
    try:
        site_mgr = SiteManager(shapefile_path=shapefile_path)
        
        wind_mgr = WindManager(
            nc_file_path=nc_file_path,
            ref_height_in=wind_config.get('ref_height_in') if wind_config is not None else None,
            hub_height_out=wind_config.get('hub_height_out') if wind_config is not None else None,
            wind_shear=wind_config.get('wind_shear') if wind_config is not None else None,
            ti=wind_config.get('ti') if wind_config is not None else None,
            discretization_aep=aep_discretization_config,
            discretization_pi=pi_discretization_config
        )
        
        floris_mgr = FlorisManager(
            wake_model_path=floris_config.get('wake_model_path') if floris_config is not None else None,
            turbine_type=floris_config.get('turbine_type') if floris_config is not None else None,
            reference_wind_height=floris_config.get('reference_wind_height') if floris_config is not None else None,
            wind_shear=floris_config.get('wind_shear') if floris_config is not None else None,
            wind_rose_aep=wind_mgr.wind_rose_aep,
            wind_rose_pi=wind_mgr.wind_rose_pi,
            dominant_wind_speed=wind_mgr.dominant_wind_speed,
            dominant_wind_direction=wind_mgr.dominant_wind_direction
        )
        
        econ_mgr = EconomicsManager(
            array_voltage=economics_config.get('array_voltage') if economics_config is not None else None,
            substation_coord=substation_coord,
            rated_power_kw=rated_power_kw,
            turbine_costs=economics_config.get('turbine_costs') if economics_config is not None else None,
            om_costs=economics_config.get('om_costs') if economics_config is not None else None,
            rental_costs=economics_config.get('rental_costs') if economics_config is not None else None,
            nominal_discount_rate=economics_config.get('nominal_discount_rate') if economics_config is not None else None,
            project_lifetime=economics_config.get('project_lifetime') if economics_config is not None else None,
            electricity_price_model=economics_config.get('electricity_price_model') if economics_config is not None else None,
            project_start_year=economics_config.get('project_start_year') if economics_config is not None else None,
            hub_height=wind_config.get('hub_height_out') if wind_config is not None else None,
            wind_speed_hub=wind_mgr.mean_hub_wind_speed,
            theta_shear=wind_config.get('wind_shear') if wind_config is not None else None
        )
        
        optimizer = LayoutOptimizer(
            site_manager=site_mgr,
            floris_manager=floris_mgr,
            econ_manager=econ_mgr,
            min_separation_m=min_distance_m,
            opt_method=optimization_config.get('opt_method') if optimization_config is not None else None
        )
        
        # Execute Top-Level Loop
        best_layout_norm, best_init_layout_norm, best_init_debug, best_n, comp_time = optimizer.run_capacity_top_loop(
            target_mw_min=target_min_mw,
            target_mw_max=target_max_mw,
            num_random_starts=num_random_starts
        )
        
        # Output final overall results
        optimizer.plot_final_solution(best_layout_norm, best_init_layout_norm, best_init_debug, best_n, comp_time)
        
    except Exception as e:
        import traceback
        print(f"Execution failed: {e}")
        traceback.print_exc()