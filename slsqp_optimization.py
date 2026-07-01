"""
slsqp_optimization.py

Runs a PI-focused SLSQP refinement on the best saved layouts for a site.
The script reuses the site, wind, FLORIS, economics, plotting, and result
writing helpers from final_assignment.py.
"""

import csv
import json
import os
import secrets
import time
import traceback

import numpy as np

from final_assignment import (
    EconomicsManager,
    FlorisManager,
    LayoutOptimizer,
    ResultWriter,
    SiteManager,
    WindManager,
)


CONFIG_PATH = "configs/kitschenrain.json"
TOP_LAYOUT_COUNT = 1


def load_config(config_path):
    with open(config_path, mode="r", encoding="utf-8") as config_file:
        return json.load(config_file)


def load_top_saved_pi_layouts(result_writer, top_count=TOP_LAYOUT_COUNT):
    def normalize_row(row):
        normalized = {}
        for key, value in row.items():
            normalized[str(key).strip()] = value
        return normalized

    if not os.path.exists(result_writer.ranking_csv_path):
        raise FileNotFoundError(
            f"Ranking CSV not found: {result_writer.ranking_csv_path}"
        )

    with open(result_writer.ranking_csv_path, mode="r", encoding="utf-8", newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        rows = [normalize_row(row) for row in reader]

    rows.sort(key=lambda row: float(row["PI"]), reverse=True)

    selected_layouts = []
    for row in rows:
        layout_id = row["L_yy_mm_dd_hh_mm_N<x>_<seed>"]
        layout_path = os.path.join(result_writer.layouts_dir, f"{layout_id}.json")
        if not os.path.exists(layout_path):
            continue

        with open(layout_path, mode="r", encoding="utf-8") as file_obj:
            payload = json.load(file_obj)

        coordinates_m = np.asarray(payload["final_coordinates_m"], dtype=float)
        if coordinates_m.ndim != 2 or coordinates_m.shape[1] != 2:
            raise ValueError(
                f"Layout {layout_id} must contain an (N, 2) final_coordinates_m array."
            )

        selected_layouts.append(
            {
                "layout_id": layout_id,
                "ranking_row": row,
                "coordinates_m": coordinates_m,
                "num_turbines": int(payload["N turbines"]),
            }
        )

        if len(selected_layouts) >= top_count:
            break

    if not selected_layouts:
        raise RuntimeError(
            f"No saved PI layouts were found under {result_writer.layouts_dir}."
        )

    return selected_layouts


def build_managers(config):
    site_config = config.get("site")
    wind_config = config.get("wind")
    turbine_config = config.get("turbine")
    optimization_config = config.get("optimization")
    floris_config = config.get("floris")
    economics_config = config.get("economics")
    substation_config = config.get("substation")

    wind_discretization_config = (
        wind_config.get("discretization") if wind_config is not None else None
    )
    aep_discretization_config = (
        wind_discretization_config.get("aep")
        if wind_discretization_config is not None
        else None
    )
    pi_discretization_config = (
        wind_discretization_config.get("pi")
        if wind_discretization_config is not None
        else None
    )

    site_id = site_config.get("site_id") if site_config is not None else None
    site_root = site_config.get("site_root") if site_config is not None else None
    shapefile_path = site_config.get("shapefile_path") if site_config is not None else None
    nc_file_path = wind_config.get("nc_file_path") if wind_config is not None else None
    turbine_diameter = turbine_config.get("diameter_m") if turbine_config is not None else None
    rated_power_kw = turbine_config.get("rated_power_kw") if turbine_config is not None else None
    min_distance_multiplier = (
        optimization_config.get("min_distance_multiplier")
        if optimization_config is not None
        else None
    )
    min_distance_m = (
        min_distance_multiplier * turbine_diameter
        if min_distance_multiplier is not None and turbine_diameter is not None
        else None
    )
    substation_coord = (
        np.array(substation_config.get("coordinates"), dtype=float)
        if substation_config is not None and substation_config.get("coordinates") is not None
        else None
    )

    result_writer = ResultWriter(site_id=site_id, site_root=site_root)
    site_mgr = SiteManager(shapefile_path=shapefile_path)

    wind_mgr = WindManager(
        nc_file_path=nc_file_path,
        ref_height_in=wind_config.get("ref_height_in") if wind_config is not None else None,
        hub_height_out=wind_config.get("hub_height_out") if wind_config is not None else None,
        wind_shear=wind_config.get("wind_shear") if wind_config is not None else None,
        ti=wind_config.get("ti") if wind_config is not None else None,
        discretization_aep=aep_discretization_config,
        discretization_pi=pi_discretization_config,
        site_id=site_id,
        weibull_distribution_path=wind_config.get("weibull_distribution_path") if wind_config is not None else None,
    )

    floris_mgr = FlorisManager(
        wake_model_path=floris_config.get("wake_model_path") if floris_config is not None else None,
        turbine_type=floris_config.get("turbine_type") if floris_config is not None else None,
        reference_wind_height=
            floris_config.get("reference_wind_height") if floris_config is not None else None,
        wind_shear=floris_config.get("wind_shear") if floris_config is not None else None,
        wind_rose_aep=wind_mgr.wind_rose_aep,
        wind_rose_pi=wind_mgr.wind_rose_pi,
        dominant_wind_speed=wind_mgr.dominant_wind_speed,
        dominant_wind_direction=wind_mgr.dominant_wind_direction,
    )

    econ_mgr = EconomicsManager(
        array_voltage=economics_config.get("array_voltage") if economics_config is not None else None,
        substation_coord=substation_coord,
        rated_power_kw=rated_power_kw,
        turbine_costs=economics_config.get("turbine_costs") if economics_config is not None else None,
        om_costs=economics_config.get("om_costs") if economics_config is not None else None,
        rental_costs=economics_config.get("rental_costs") if economics_config is not None else None,
        nominal_discount_rate=
            economics_config.get("nominal_discount_rate") if economics_config is not None else None,
        project_lifetime=economics_config.get("project_lifetime") if economics_config is not None else None,
        electricity_price_model=
            economics_config.get("electricity_price_model") if economics_config is not None else None,
        project_start_year=economics_config.get("project_start_year") if economics_config is not None else None,
        hub_height=wind_config.get("hub_height_out") if wind_config is not None else None,
        wind_speed_bins=wind_mgr.wind_rose_pi.wind_speeds,
        theta_shear=wind_config.get("wind_shear") if wind_config is not None else None,
    )

    optimizer = LayoutOptimizer(
        site_manager=site_mgr,
        floris_manager=floris_mgr,
        econ_manager=econ_mgr,
        min_separation_m=min_distance_m,
        opt_method="SLSQP",
        aep_maxiter=optimization_config.get("aep_maxiter", 100)
        if optimization_config is not None
        else 100,
        pi_maxiter=2000 # Not config derived!
        if optimization_config is not None
        else 200,
    )

    return result_writer, optimizer, site_id, site_mgr


def run_slsqp_on_saved_layouts(config_path=CONFIG_PATH):
    config = load_config(config_path)
    result_writer, optimizer, site_id, site_mgr = build_managers(config)
    saved_layouts = load_top_saved_pi_layouts(result_writer, top_count=TOP_LAYOUT_COUNT)

    best_result = None
    best_pi = -np.inf

    for index, saved_layout in enumerate(saved_layouts, start=1):
        num_turbines = saved_layout["num_turbines"]
        start_layout_real = saved_layout["coordinates_m"]
        start_layout_norm = site_mgr.normalize_coords(start_layout_real)

        if not optimizer._layout_is_feasible(start_layout_norm):
            raise ValueError(
                f"Saved layout {saved_layout['layout_id']} is not feasible in normalized space."
            )

        seed = secrets.randbits(64)
        layout_id = result_writer.build_layout_id(num_turbines=num_turbines, seed=seed)

        print(
            f"[SLSQP {index}/{len(saved_layouts)}] Starting from {saved_layout['layout_id']} -> {layout_id}"
        )

        start_time = time.time()
        final_layout_norm, local_pi = optimizer.run_optimization(start_layout_norm, num_turbines)
        elapsed = time.time() - start_time

        optimizer.plot_final_solution(
            final_layout_norm,
            start_layout_norm,
            init_debug=None,
            num_turbines=num_turbines,
            total_time=elapsed,
            result_writer=result_writer,
            layout_id=layout_id,
            seed=seed,
            site_id=site_id,
            show_plots=False,
        )

        print(
            f"[SLSQP {index}/{len(saved_layouts)}] Finished in {elapsed:.2f}s with PI={local_pi:.6f}"
        )

        if local_pi > best_pi:
            best_pi = local_pi
            best_result = {
                "layout_id": layout_id,
                "seed": seed,
                "num_turbines": num_turbines,
                "elapsed": elapsed,
                "pi": local_pi,
            }

    if best_result is not None:
        print(
            f"Best SLSQP result: {best_result['layout_id']} "
            f"(N={best_result['num_turbines']}, PI={best_result['pi']:.6f}, "
            f"time={best_result['elapsed']:.2f}s)"
        )


if __name__ == "__main__":
    try:
        run_slsqp_on_saved_layouts()
    except Exception as exc:
        print(f"Execution failed: {exc}")
        traceback.print_exc()