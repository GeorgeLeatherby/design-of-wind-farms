"""
layout_and_table_metrics_generator.py

Standalone utility for an existing saved layout id:
1) Regenerates and overwrites the 3 PNG figures from LayoutOptimizer.plot_final_solution.
2) Writes a detailed verification workbook with LandBOSSE, FLORIS, and year-by-year
   financial values used by the existing calculation formulas.
"""

import json
import os
import csv

import numpy as np
import pandas as pd

from external.landbosse.landbosse.main_function import run_landbosse
from slsqp_optimization import build_managers, load_config


CONFIG_PATH = "configs/waidmannsheil.json"
LAYOUT_ID = "L_26_06_18_14_39_N17_11057970192623874460"


class LayoutFigureResultWriter:
    """
    Minimal writer adapter used only to save the 3 figure PNG files into
    <site>/results/layouts while keeping the original naming convention.
    """

    def __init__(self, base_result_writer):
        self.figures_dir = base_result_writer.figures_dir
        self.ranking_csv_path = base_result_writer.ranking_csv_path
        self.ranking_columns = list(base_result_writer.ranking_columns)

    def save_layout_json(self, layout_id, data):
        _ = (layout_id, data)

    def update_ranking(self, ranking_entry):
        def normalize_row(row):
            normalized = {}
            for key, value in row.items():
                normalized[str(key).strip()] = value
            return normalized

        rows = []
        if os.path.exists(self.ranking_csv_path):
            with open(self.ranking_csv_path, mode="r", encoding="utf-8", newline="") as file_obj:
                reader = csv.DictReader(file_obj)
                rows = [normalize_row(row) for row in reader]

        incoming = normalize_row(ranking_entry)
        key_name = "L_yy_mm_dd_hh_mm_N<x>_<seed>"
        key_value = incoming.get(key_name)

        replaced = False
        for idx, row in enumerate(rows):
            if row.get(key_name) == key_value:
                rows[idx] = incoming
                replaced = True
                break

        if not replaced:
            rows.append(incoming)

        rows.sort(key=lambda row: float(row["PI"]), reverse=True)
        rows = [{column: row.get(column, "") for column in self.ranking_columns} for row in rows]

        with open(self.ranking_csv_path, mode="w", encoding="utf-8", newline="") as file_obj:
            writer = csv.DictWriter(file_obj, fieldnames=self.ranking_columns)
            writer.writeheader()
            writer.writerows(rows)

    def save_figures(self, layout_id, seed, fig_map, fig_wake, fig_table):
        layout_prefix = layout_id.rsplit("_", 1)[0]
        map_path = os.path.join(self.figures_dir, f"{layout_prefix}_map_{seed}.png")
        wake_path = os.path.join(self.figures_dir, f"{layout_prefix}_wake_{seed}.png")
        table_path = os.path.join(self.figures_dir, f"{layout_prefix}_table_{seed}.png")

        fig_map.savefig(map_path, dpi=150)
        fig_wake.savefig(wake_path, dpi=150)
        fig_table.savefig(table_path, dpi=150)

        print("Saved figure files:")
        print(f" - {map_path}")
        print(f" - {wake_path}")
        print(f" - {table_path}")


def _load_saved_layout_payload(result_writer, layout_id):
    layout_path = os.path.join(result_writer.layouts_dir, f"{layout_id}.json")
    if not os.path.exists(layout_path):
        raise FileNotFoundError(f"Layout JSON not found: {layout_path}")

    with open(layout_path, mode="r", encoding="utf-8") as file_obj:
        payload = json.load(file_obj)

    final_coordinates_m = np.asarray(payload.get("final_coordinates_m"), dtype=float)
    if final_coordinates_m.ndim != 2 or final_coordinates_m.shape[1] != 2:
        raise ValueError(
            f"Layout {layout_id} must contain final_coordinates_m with shape (N, 2)."
        )

    initial_coordinates_m = payload.get("initial_coordinates_m")
    if initial_coordinates_m is None:
        initial_coordinates_m = final_coordinates_m.copy()
    else:
        initial_coordinates_m = np.asarray(initial_coordinates_m, dtype=float)

    num_turbines = int(payload.get("N turbines", final_coordinates_m.shape[0]))
    seed = payload.get("seed")
    if seed is None:
        try:
            seed = int(layout_id.rsplit("_", 1)[-1])
        except ValueError:
            seed = 0

    return payload, final_coordinates_m, initial_coordinates_m, num_turbines, int(seed)


def _build_financial_tables(econ_mgr, layout_real, num_turbines, aep_wake_wh, energy_rose_wh, landbosse_df):
    bos_cost_total = float(landbosse_df["Cost per project"].sum())
    aep_mwh = float(aep_wake_wh / 1e6)
    aep_kwh = float(aep_wake_wh / 1000)
    total_capacity_mw = float((econ_mgr.rated_power_kw / 1000.0) * num_turbines)

    energy_rose_wh = np.asarray(energy_rose_wh, dtype=float)
    energy_rose_mwh = energy_rose_wh / 1e6
    energy_by_wind_speed_mwh = np.sum(energy_rose_mwh, axis=0)

    turbine_cost_total = float(econ_mgr.turbine_costs * total_capacity_mw)
    initial_investment = float(turbine_cost_total + bos_cost_total)
    annual_om_cost = float((econ_mgr.om_costs * aep_kwh) + (econ_mgr.rental_costs * total_capacity_mw))

    d = float(econ_mgr.nominal_discount_rate)
    n = int(econ_mgr.project_lifetime)

    discounted_energy_total = 0.0
    discounted_om_total = 0.0
    discounted_net_cash_flow_total = 0.0

    year_rows = []
    cumulative_discounted_net_cash_flow = 0.0
    cumulative_npv_after_capex = -initial_investment
    ws_price_rows = []

    for year_offset in range(n):
        year = int(econ_mgr.project_start_year + year_offset)
        spot_price_by_wind_speed = np.asarray(
            econ_mgr._get_spot_price_vector_for_year(year), dtype=float
        )
        annual_revenue = float(np.dot(energy_by_wind_speed_mwh, spot_price_by_wind_speed))
        annual_net_cash_flow = float(annual_revenue - annual_om_cost)

        discount_factor = float(1.0 / ((1.0 + d) ** (year_offset + 1)))
        discounted_energy = float(aep_mwh * discount_factor)
        discounted_om = float(annual_om_cost * discount_factor)
        discounted_ncf = float(annual_net_cash_flow * discount_factor)

        discounted_energy_total += discounted_energy
        discounted_om_total += discounted_om
        discounted_net_cash_flow_total += discounted_ncf

        cumulative_discounted_net_cash_flow += discounted_ncf
        cumulative_npv_after_capex += discounted_ncf

        year_rows.append(
            {
                "year": year,
                "annual_revenue_usd": annual_revenue,
                "annual_om_cost_usd": annual_om_cost,
                "annual_net_cash_flow_usd": annual_net_cash_flow,
                "discount_factor": discount_factor,
                "discounted_energy_mwh": discounted_energy,
                "discounted_om_cost_usd": discounted_om,
                "discounted_net_cash_flow_usd": discounted_ncf,
                "cumulative_discounted_net_cash_flow_usd": cumulative_discounted_net_cash_flow,
                "npv_after_capex_usd": cumulative_npv_after_capex,
            }
        )

        price_row = {"year": year}
        for ws, price in zip(econ_mgr.wind_speed_bins, spot_price_by_wind_speed):
            price_row[f"ws_{float(ws):g}_usd_per_mwh"] = float(price)
        ws_price_rows.append(price_row)

    lcoe = float((initial_investment + discounted_om_total) / discounted_energy_total)
    pi = float(discounted_net_cash_flow_total / initial_investment)

    summary_df = pd.DataFrame(
        [
            {"metric": "aep_wake_wh", "value": float(aep_wake_wh)},
            {"metric": "aep_mwh", "value": aep_mwh},
            {"metric": "bos_cost_total_usd", "value": bos_cost_total},
            {"metric": "turbine_cost_total_usd", "value": turbine_cost_total},
            {"metric": "initial_investment_usd", "value": initial_investment},
            {"metric": "annual_om_cost_usd", "value": annual_om_cost},
            {"metric": "discounted_energy_total_mwh", "value": float(discounted_energy_total)},
            {"metric": "discounted_om_total_usd", "value": float(discounted_om_total)},
            {"metric": "discounted_net_cash_flow_total_usd", "value": float(discounted_net_cash_flow_total)},
            {"metric": "lcoe_usd_per_mwh", "value": lcoe},
            {"metric": "pi", "value": pi},
        ]
    )

    year_df = pd.DataFrame(year_rows)
    energy_by_ws_df = pd.DataFrame(
        {
            "wind_speed_bin": np.asarray(econ_mgr.wind_speed_bins, dtype=float),
            "energy_by_wind_speed_mwh": np.asarray(energy_by_wind_speed_mwh, dtype=float),
        }
    )
    spot_price_df = pd.DataFrame(ws_price_rows)

    return summary_df, year_df, energy_by_ws_df, spot_price_df


def _build_floris_tables(floris_mgr, aep_wake_wh, aep_no_wake_wh, energy_rose_wh):
    energy_rose_wh = np.asarray(energy_rose_wh, dtype=float)
    aep_from_energy_rose_wh = float(np.nansum(energy_rose_wh))

    ws_bins = np.asarray(floris_mgr.wind_rose_pi.wind_speeds, dtype=float)
    wd_bins = np.asarray(floris_mgr.wind_rose_pi.wind_directions, dtype=float)

    if energy_rose_wh.shape[1] != ws_bins.shape[0]:
        ws_labels = [f"ws_col_{idx}" for idx in range(energy_rose_wh.shape[1])]
    else:
        ws_labels = [f"ws_{float(ws):g}" for ws in ws_bins]

    if energy_rose_wh.shape[0] != wd_bins.shape[0]:
        wd_labels = [f"wd_row_{idx}" for idx in range(energy_rose_wh.shape[0])]
    else:
        wd_labels = [f"wd_{float(wd):g}" for wd in wd_bins]

    floris_summary_df = pd.DataFrame(
        [
            {"metric": "aep_wake_wh", "value": float(aep_wake_wh)},
            {"metric": "aep_no_wake_wh", "value": float(aep_no_wake_wh)},
            {"metric": "aep_from_energy_rose_wh", "value": aep_from_energy_rose_wh},
        ]
    )
    energy_rose_df = pd.DataFrame(energy_rose_wh, index=wd_labels, columns=ws_labels)
    energy_rose_df.index.name = "wind_direction_bin"

    return floris_summary_df, energy_rose_df


def regenerate_layout_figures_and_metrics(config_path=CONFIG_PATH, layout_id=LAYOUT_ID):
    if layout_id == "L_yy_mm_dd_hh_mm_N<x>_<seed>":
        raise ValueError("Please set LAYOUT_ID at the top of the script before running.")

    config = load_config(config_path)
    result_writer, optimizer, site_id, site_mgr = build_managers(config)

    (
        payload,
        final_coordinates_m,
        initial_coordinates_m,
        num_turbines,
        seed,
    ) = _load_saved_layout_payload(result_writer, layout_id)

    final_layout_norm = site_mgr.normalize_coords(final_coordinates_m)
    initial_layout_norm = site_mgr.normalize_coords(initial_coordinates_m)

    layout_writer = LayoutFigureResultWriter(result_writer)

    optimizer.plot_final_solution(
        final_layout_norm,
        initial_layout_norm,
        init_debug=None,
        num_turbines=num_turbines,
        total_time=0.0,
        result_writer=layout_writer,
        layout_id=layout_id,
        seed=seed,
        site_id=site_id,
        show_plots=False,
    )

    final_layout_real = final_coordinates_m
    aep_wake_wh, aep_no_wake_wh, energy_rose_wh = optimizer.floris.evaluate_layout_pi(final_layout_real)

    landbosse_df = run_landbosse(
        Turbine_coordinates=final_layout_real,
        Substation_coordinate=optimizer.econ.substation_coord,
        Desired_Voltage=optimizer.econ.array_voltage,
        WriteExcel=False,
        Display=False,
    )

    floris_summary_df, energy_rose_df = _build_floris_tables(
        floris_mgr=optimizer.floris,
        aep_wake_wh=aep_wake_wh,
        aep_no_wake_wh=aep_no_wake_wh,
        energy_rose_wh=energy_rose_wh,
    )

    financial_summary_df, year_df, energy_by_ws_df, spot_price_df = _build_financial_tables(
        econ_mgr=optimizer.econ,
        layout_real=final_layout_real,
        num_turbines=num_turbines,
        aep_wake_wh=aep_wake_wh,
        energy_rose_wh=energy_rose_wh,
        landbosse_df=landbosse_df,
    )

    excel_path = os.path.join(result_writer.results_dir, f"{layout_id}_calculated_metrics.xlsx")
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        landbosse_df.to_excel(writer, sheet_name="LandBOSSE", index=False)

        floris_summary_df.to_excel(writer, sheet_name="Floris", index=False, startrow=0)
        energy_rose_df.to_excel(
            writer,
            sheet_name="Floris",
            startrow=len(floris_summary_df) + 2,
            index=True,
        )

        financial_summary_df.to_excel(writer, sheet_name="YearbyYear", index=False, startrow=0)
        year_df.to_excel(
            writer,
            sheet_name="YearbyYear",
            index=False,
            startrow=len(financial_summary_df) + 2,
        )
        energy_by_ws_df.to_excel(
            writer,
            sheet_name="YearbyYear",
            index=False,
            startrow=len(financial_summary_df) + len(year_df) + 5,
        )
        spot_price_df.to_excel(
            writer,
            sheet_name="YearbyYear",
            index=False,
            startrow=len(financial_summary_df) + len(year_df) + len(energy_by_ws_df) + 8,
        )

    print(f"Saved workbook: {excel_path}")
    print(f"Used layout source file: {os.path.join(result_writer.layouts_dir, f'{layout_id}.json')}")
    print(f"Site id: {site_id}")
    print(f"Layout payload fields: {sorted(payload.keys())}")


if __name__ == "__main__":
    regenerate_layout_figures_and_metrics()