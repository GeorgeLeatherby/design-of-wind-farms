"""
windrose_from_config.py

Standalone utility to generate wind rose graph(s) from one config file.
It reuses WindManager from final_assignment.py so the exact same data source
selection logic is used:
- nc_file_path for regular sites
- weibull_distribution_path for denmark when nc_file_path is null

Usage:
  python windrose_from_config.py --config configs/denmark.json
"""

import argparse
import json
import os

import matplotlib.pyplot as plt

from final_assignment import WindManager


def _load_config(config_path):
    with open(config_path, mode="r", encoding="utf-8") as cfg_file:
        return json.load(cfg_file)


def _build_discretization_items(wind_cfg):
    discret_cfg = wind_cfg.get("discretization") if wind_cfg is not None else None
    if discret_cfg is None:
        return []

    items = []
    if isinstance(discret_cfg, dict):
        # Preferred structure: {"aep": {...}, "pi": {...}}
        if "aep" in discret_cfg or "pi" in discret_cfg:
            if discret_cfg.get("aep") is not None:
                items.append(("aep", discret_cfg.get("aep")))
            if discret_cfg.get("pi") is not None:
                items.append(("pi", discret_cfg.get("pi")))
        else:
            # Fallback: single discretization dictionary
            items.append(("single", discret_cfg))
    return items


def _build_wind_manager_from_config(config):
    site_cfg = config.get("site") if config is not None else None
    wind_cfg = config.get("wind") if config is not None else None

    discret_items = _build_discretization_items(wind_cfg)
    if not discret_items:
        raise ValueError("No wind discretization found in config wind.discretization.")

    # WindManager requires both stages; for single-discretization inputs,
    # we pass the same config to both.
    d_aep = discret_items[0][1]
    d_pi = discret_items[-1][1]

    return WindManager(
        nc_file_path=wind_cfg.get("nc_file_path") if wind_cfg is not None else None,
        ref_height_in=wind_cfg.get("ref_height_in") if wind_cfg is not None else None,
        hub_height_out=wind_cfg.get("hub_height_out") if wind_cfg is not None else None,
        wind_shear=wind_cfg.get("wind_shear") if wind_cfg is not None else None,
        ti=wind_cfg.get("ti") if wind_cfg is not None else None,
        discretization_aep=d_aep,
        discretization_pi=d_pi,
        site_id=site_cfg.get("site_id") if site_cfg is not None else None,
        weibull_distribution_path=wind_cfg.get("weibull_distribution_path") if wind_cfg is not None else None,
    )


def _infer_data_source_text(wind_cfg):
    nc_path = wind_cfg.get("nc_file_path") if wind_cfg is not None else None
    wb_path = wind_cfg.get("weibull_distribution_path") if wind_cfg is not None else None

    if nc_path:
        return f"Data source: nc_file_path = {nc_path}"
    if wb_path:
        return f"Data source: weibull_distribution_path = {wb_path}"
    return "Data source: unknown (neither nc_file_path nor weibull_distribution_path is set)"


def generate_windrose_graphs(config_path, output_dir=None, show=False):
    config = _load_config(config_path)
    site_cfg = config.get("site") if config is not None else None
    wind_cfg = config.get("wind") if config is not None else None

    site_id = site_cfg.get("site_id", "site") if site_cfg is not None else "site"
    source_text = _infer_data_source_text(wind_cfg)

    wind_mgr = _build_wind_manager_from_config(config)
    discret_items = _build_discretization_items(wind_cfg)

    rose_by_label = {
        "aep": wind_mgr.wind_rose_aep,
        "pi": wind_mgr.wind_rose_pi,
        "single": wind_mgr.wind_rose_pi,
    }

    out_dir = output_dir if output_dir is not None else os.path.join(site_id, "results", "figures")
    os.makedirs(out_dir, exist_ok=True)

    generated_paths = []

    for label, discret in discret_items:
        d_wd = discret.get("d_wd") if isinstance(discret, dict) else "?"
        d_ws = discret.get("d_ws") if isinstance(discret, dict) else "?"
        rose = rose_by_label[label]

        # Use FLORIS built-in plotting on the WindRose object.
        rose.plot(ws_step=d_ws, wd_step=d_wd)
        fig = plt.gcf()
        ax = plt.gca()
        ax.set_title(
            f"Wind Rose ({label.upper()} discretization: d_wd={d_wd}, d_ws={d_ws})\n{source_text}"
        )
        fig.tight_layout()

        out_path = os.path.join(out_dir, f"{site_id}_wind_rose_{label}.png")
        fig.savefig(out_path, dpi=300)
        generated_paths.append(out_path)

        if show:
            plt.show()
        else:
            plt.close(fig)

    print("Generated wind rose graphs:")
    for p in generated_paths:
        print(f" - {p}")


def main():
    parser = argparse.ArgumentParser(description="Generate wind rose graph(s) from one config file.")
    parser.add_argument("--config", default="configs/denmark.json", help="Path to site config JSON.")
    parser.add_argument("--output-dir", default=None, help="Optional output directory.")
    parser.add_argument("--show", action="store_true", help="Show figures interactively.")
    args = parser.parse_args()

    generate_windrose_graphs(config_path=args.config, output_dir=args.output_dir, show=args.show)


if __name__ == "__main__":
    main()
